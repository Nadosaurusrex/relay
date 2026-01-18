"""
Unit tests for core authentication functions.

Tests the core auth utilities without requiring database setup.
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta

from gateway.core.auth import (
    generate_api_key,
    hash_api_key,
    verify_api_key,
    generate_jwt,
    decode_jwt,
    AuthContext
)
from gateway.config import get_settings


class TestAPIKeyGeneration:
    """Tests for API key generation and verification."""

    def test_generate_api_key_format(self):
        """Test that generated API keys have correct format."""
        api_key = generate_api_key()

        # Should start with relay prefix
        assert api_key.startswith("rly_sk_")

        # Should be 71 characters total (rly_sk_ + 64 hex chars)
        assert len(api_key) == 71

        # Should be different each time
        api_key2 = generate_api_key()
        assert api_key != api_key2

    def test_api_key_hashing(self):
        """Test API key hashing with bcrypt."""
        api_key = "rly_sk_test_key_12345"

        hashed = hash_api_key(api_key)

        # Should be a bcrypt hash (starts with $2b$)
        assert hashed.startswith("$2b$")

        # Should be different each time (different salt)
        hashed2 = hash_api_key(api_key)
        assert hashed != hashed2

    def test_api_key_verification_success(self):
        """Test successful API key verification."""
        api_key = "rly_sk_test_key_12345"
        hashed = hash_api_key(api_key)

        # Should verify successfully
        assert verify_api_key(api_key, hashed) is True

    def test_api_key_verification_failure(self):
        """Test failed API key verification with wrong key."""
        api_key = "rly_sk_test_key_12345"
        wrong_key = "rly_sk_wrong_key_99999"
        hashed = hash_api_key(api_key)

        # Should fail verification
        assert verify_api_key(wrong_key, hashed) is False

    def test_api_key_verification_invalid_hash(self):
        """Test API key verification with invalid hash format."""
        api_key = "rly_sk_test_key_12345"
        invalid_hash = "not_a_valid_hash"

        # Should handle gracefully and return False
        assert verify_api_key(api_key, invalid_hash) is False


class TestJWTGeneration:
    """Tests for JWT token generation and verification."""

    @pytest.fixture(autouse=True)
    def clear_settings_cache(self):
        """Clear settings cache before each test."""
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()

    @pytest.fixture
    def jwt_secret(self, monkeypatch):
        """Set JWT secret for testing."""
        monkeypatch.setenv("RELAY_JWT_SECRET", "test_secret_key_for_testing")
        monkeypatch.setenv("RELAY_JWT_EXPIRY_HOURS", "1")
        monkeypatch.setenv("RELAY_AUTH_REQUIRED", "false")
        # Clear cache after setting env vars
        get_settings.cache_clear()

    def test_generate_jwt(self, jwt_secret):
        """Test JWT generation."""
        agent_id = "agent_test123"
        org_id = "org_test456"

        token = generate_jwt(agent_id, org_id)

        # Should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0

        # Should be a valid JWT (has 3 parts separated by dots)
        parts = token.split(".")
        assert len(parts) == 3

    def test_decode_jwt(self, jwt_secret):
        """Test JWT decoding."""
        agent_id = "agent_test123"
        org_id = "org_test456"

        token = generate_jwt(agent_id, org_id)

        # Decode without validation to check payload
        import jwt as pyjwt
        payload = pyjwt.decode(token, options={"verify_signature": False})

        # Should contain correct claims
        assert payload["agent_id"] == agent_id
        assert payload["org_id"] == org_id
        assert "iat" in payload
        assert "exp" in payload

    def test_jwt_expiry(self, jwt_secret):
        """Test that JWT has correct expiry."""
        agent_id = "agent_test123"
        org_id = "org_test456"

        token = generate_jwt(agent_id, org_id)

        # Decode without validation to check timestamps
        import jwt as pyjwt
        payload = pyjwt.decode(token, options={"verify_signature": False})

        # EXP should be approximately 1 hour after IAT
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])

        time_diff = exp_time - iat_time
        assert 3590 <= time_diff.total_seconds() <= 3610  # Allow 10 second variance

    def test_decode_invalid_jwt(self, jwt_secret):
        """Test decoding invalid JWT."""
        with pytest.raises(jwt.InvalidTokenError):
            decode_jwt("invalid.token.here")

    def test_decode_expired_jwt(self, jwt_secret, monkeypatch):
        """Test decoding expired JWT."""
        # Create a token that's manually expired
        agent_id = "agent_test123"
        org_id = "org_test456"

        # Create a token with past expiry
        import jwt as pyjwt
        from gateway.config import get_settings
        settings = get_settings()

        now = time.time()
        payload = {
            "agent_id": agent_id,
            "org_id": org_id,
            "iat": int(now - 3600),  # 1 hour ago
            "exp": int(now - 10)  # Expired 10 seconds ago
        }

        token = pyjwt.encode(payload, settings.jwt_secret, algorithm="HS256")

        # Should raise ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_jwt(token)

    def test_jwt_with_wrong_secret(self, jwt_secret, monkeypatch):
        """Test JWT verification with wrong secret."""
        agent_id = "agent_test123"
        org_id = "org_test456"

        token = generate_jwt(agent_id, org_id)

        # Change the secret
        monkeypatch.setenv("RELAY_JWT_SECRET", "different_secret")
        get_settings.cache_clear()

        # Should raise InvalidSignatureError
        with pytest.raises(jwt.InvalidSignatureError):
            decode_jwt(token)

    def test_jwt_missing_secret(self, monkeypatch):
        """Test JWT generation without secret configured."""
        monkeypatch.delenv("RELAY_JWT_SECRET", raising=False)
        get_settings.cache_clear()

        with pytest.raises(ValueError, match="JWT secret not configured"):
            generate_jwt("agent_test", "org_test")


class TestAuthContext:
    """Tests for AuthContext class."""

    def test_auth_context_creation(self):
        """Test creating AuthContext."""
        agent_id = "agent_test123"
        org_id = "org_test456"

        context = AuthContext(agent_id, org_id)

        assert context.agent_id == agent_id
        assert context.org_id == org_id

    def test_auth_context_repr(self):
        """Test AuthContext string representation."""
        context = AuthContext("agent_test", "org_test")

        repr_str = repr(context)
        assert "AuthContext" in repr_str
        assert "agent_test" in repr_str
        assert "org_test" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
