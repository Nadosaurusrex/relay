"""
Integration tests for V1 Agent Authorization & Audit System.

Tests the complete end-to-end authentication and authorization flow:
1. Register organization
2. Get JWT token
3. Register additional agents
4. Submit manifest with JWT auth
5. Query audit trail with org-scoped filtering
6. Test security controls (org isolation, invalid tokens, etc.)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gateway.main import app
from gateway.db.models import Base
from gateway.db.session import get_db


# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test database engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh database for each test.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def jwt_secret(monkeypatch):
    """Set JWT secret for testing."""
    monkeypatch.setenv("RELAY_JWT_SECRET", "test_secret_key_for_testing_only")
    monkeypatch.setenv("RELAY_AUTH_REQUIRED", "true")


class TestAuthEndToEnd:
    """End-to-end tests for authentication and authorization."""

    def test_complete_auth_flow(self, test_db, jwt_secret):
        """
        Test the complete authentication flow:
        1. Register organization → get initial agent API key
        2. Obtain JWT token using API key
        3. Register additional agent using JWT
        4. List agents using JWT
        5. Get organization info using JWT
        """
        # Step 1: Register organization
        org_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Test Corp",
                "contact_email": "admin@test.com"
            }
        )
        assert org_response.status_code == 200
        org_data = org_response.json()

        assert "org_id" in org_data
        assert org_data["org_name"] == "Test Corp"
        assert "initial_agent" in org_data

        org_id = org_data["org_id"]
        initial_agent_id = org_data["initial_agent"]["agent_id"]
        api_key = org_data["initial_agent"]["api_key"]

        assert api_key.startswith("rly_sk_")

        # Step 2: Obtain JWT token
        token_response = client.post(
            "/v1/auth/token",
            json={
                "agent_id": initial_agent_id,
                "api_key": api_key
            }
        )
        assert token_response.status_code == 200
        token_data = token_response.json()

        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["expires_in"] == 3600

        access_token = token_data["access_token"]

        # Step 3: Register additional agent
        agent_response = client.post(
            "/v1/agents/register",
            json={
                "agent_name": "sales-bot",
                "description": "Handles quote approvals"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert agent_response.status_code == 200
        agent_data = agent_response.json()

        assert agent_data["org_id"] == org_id
        assert agent_data["agent_name"] == "sales-bot"
        assert "api_key" in agent_data

        # Step 4: List agents
        list_response = client.get(
            "/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert list_response.status_code == 200
        list_data = list_response.json()

        assert list_data["total"] == 2  # Initial admin + sales-bot
        assert len(list_data["agents"]) == 2

        # Step 5: Get organization info
        org_info_response = client.get(
            f"/v1/orgs/{org_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert org_info_response.status_code == 200
        org_info = org_info_response.json()

        assert org_info["org_id"] == org_id
        assert org_info["agents_count"] == 2

    def test_invalid_api_key_authentication(self, test_db, jwt_secret):
        """Test that invalid API key is rejected."""
        # Register organization
        org_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Test Corp",
                "contact_email": "admin@test.com"
            }
        )
        org_data = org_response.json()
        agent_id = org_data["initial_agent"]["agent_id"]

        # Try to authenticate with invalid API key
        token_response = client.post(
            "/v1/auth/token",
            json={
                "agent_id": agent_id,
                "api_key": "rly_sk_invalid_key"
            }
        )
        assert token_response.status_code == 401
        assert "Invalid credentials" in token_response.json()["detail"]

    def test_expired_or_invalid_jwt(self, test_db, jwt_secret):
        """Test that invalid JWT is rejected."""
        # Try to access protected endpoint with invalid JWT
        response = client.get(
            "/v1/agents",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_org_isolation(self, test_db, jwt_secret):
        """
        Test that organizations are properly isolated.
        One org cannot access another org's resources.
        """
        # Register first organization
        org1_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Org 1",
                "contact_email": "admin1@test.com"
            }
        )
        org1_data = org1_response.json()
        org1_id = org1_data["org_id"]
        org1_api_key = org1_data["initial_agent"]["api_key"]
        org1_agent_id = org1_data["initial_agent"]["agent_id"]

        # Register second organization
        org2_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Org 2",
                "contact_email": "admin2@test.com"
            }
        )
        org2_data = org2_response.json()
        org2_id = org2_data["org_id"]

        # Get JWT for org1
        token_response = client.post(
            "/v1/auth/token",
            json={
                "agent_id": org1_agent_id,
                "api_key": org1_api_key
            }
        )
        org1_token = token_response.json()["access_token"]

        # Try to access org2's info with org1's token
        response = client.get(
            f"/v1/orgs/{org2_id}",
            headers={"Authorization": f"Bearer {org1_token}"}
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_missing_jwt_when_auth_required(self, test_db, jwt_secret):
        """Test that protected endpoints require JWT when auth_required=true."""
        # Try to access protected endpoint without JWT
        response = client.get("/v1/agents")
        assert response.status_code == 401
        assert "Authorization token required" in response.json()["detail"]

    def test_backward_compatibility_no_auth_required(self, test_db, monkeypatch):
        """
        Test backward compatibility mode (auth_required=false).

        When auth_required=false, endpoints should work without JWT.
        """
        # Set auth_required to false
        monkeypatch.setenv("RELAY_AUTH_REQUIRED", "false")
        monkeypatch.setenv("RELAY_JWT_SECRET", "test_secret")

        # Access protected endpoint without JWT (should work)
        response = client.get("/v1/agents")
        # Note: This will return empty list since no agents exist, but shouldn't fail auth
        assert response.status_code == 200

    def test_auth_event_logging(self, test_db, jwt_secret):
        """Test that authentication events are logged to audit trail."""
        from gateway.db.models import AuthEvent
        from gateway.db.session import get_db

        # Register organization
        org_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Test Corp",
                "contact_email": "admin@test.com"
            }
        )
        org_data = org_response.json()
        agent_id = org_data["initial_agent"]["agent_id"]
        api_key = org_data["initial_agent"]["api_key"]

        # Authenticate successfully
        token_response = client.post(
            "/v1/auth/token",
            json={
                "agent_id": agent_id,
                "api_key": api_key
            }
        )
        assert token_response.status_code == 200

        # Try to authenticate with invalid key
        client.post(
            "/v1/auth/token",
            json={
                "agent_id": agent_id,
                "api_key": "rly_sk_invalid"
            }
        )

        # Check that auth events were logged
        db = next(override_get_db())
        auth_events = db.query(AuthEvent).all()

        # Should have at least 2 events: 1 success, 1 failure
        assert len(auth_events) >= 2

        # Check successful event
        success_events = [e for e in auth_events if e.success and e.event_type == "authentication"]
        assert len(success_events) >= 1

        # Check failed event
        failed_events = [e for e in auth_events if not e.success and e.event_type == "authentication"]
        assert len(failed_events) >= 1
        assert "Invalid API key" in failed_events[0].failure_reason


class TestManifestAuthIntegration:
    """Integration tests for manifest validation with authentication."""

    def test_manifest_validation_with_auth(self, test_db, jwt_secret):
        """
        Test manifest validation with authentication.

        Note: This test may fail if OPA or other dependencies are not available.
        We're mainly testing the auth integration here.
        """
        # Register organization
        org_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Test Corp",
                "contact_email": "admin@test.com"
            }
        )
        org_data = org_response.json()
        org_id = org_data["org_id"]
        agent_id = org_data["initial_agent"]["agent_id"]
        api_key = org_data["initial_agent"]["api_key"]

        # Get JWT token
        token_response = client.post(
            "/v1/auth/token",
            json={
                "agent_id": agent_id,
                "api_key": api_key
            }
        )
        access_token = token_response.json()["access_token"]

        # Try to submit manifest with matching org_id
        manifest_response = client.post(
            "/v1/manifest/validate",
            json={
                "manifest": {
                    "agent": {
                        "agent_id": agent_id,
                        "org_id": org_id,
                        "user_id": "user@test.com"
                    },
                    "action": {
                        "provider": "stripe",
                        "method": "create_payment",
                        "parameters": {
                            "amount": 1000,
                            "currency": "USD"
                        }
                    },
                    "justification": {
                        "reasoning": "Test payment"
                    }
                },
                "dry_run": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        # Will fail if OPA is not available, but auth should pass
        assert manifest_response.status_code in [200, 503]  # 503 if OPA unavailable

    def test_manifest_org_mismatch(self, test_db, jwt_secret):
        """Test that manifest with different org_id is rejected."""
        # Register organization
        org_response = client.post(
            "/v1/orgs/register",
            json={
                "org_name": "Test Corp",
                "contact_email": "admin@test.com"
            }
        )
        org_data = org_response.json()
        agent_id = org_data["initial_agent"]["agent_id"]
        api_key = org_data["initial_agent"]["api_key"]

        # Get JWT token
        token_response = client.post(
            "/v1/auth/token",
            json={
                "agent_id": agent_id,
                "api_key": api_key
            }
        )
        access_token = token_response.json()["access_token"]

        # Try to submit manifest with different org_id
        manifest_response = client.post(
            "/v1/manifest/validate",
            json={
                "manifest": {
                    "agent": {
                        "agent_id": "different_agent",
                        "org_id": "different_org",
                        "user_id": "user@test.com"
                    },
                    "action": {
                        "provider": "stripe",
                        "method": "create_payment",
                        "parameters": {
                            "amount": 1000,
                            "currency": "USD"
                        }
                    },
                    "justification": {
                        "reasoning": "Test payment"
                    }
                },
                "dry_run": True
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert manifest_response.status_code == 403
        assert "Organization mismatch" in manifest_response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
