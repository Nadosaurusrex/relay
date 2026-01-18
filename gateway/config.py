"""
Configuration management for Relay Gateway.

Uses Pydantic Settings for environment-based configuration.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Gateway configuration settings.

    Can be overridden via environment variables (e.g., RELAY_OPA_URL).
    """

    # Application
    app_name: str = "Relay Gateway"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "relay"
    db_user: str = "relay"
    db_password: str = "relay_password"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # OPA Policy Engine
    opa_url: str = "http://localhost:8181"
    policy_path: str = "relay/policies/main"
    policy_version: str = "v1.0.0"

    # Cryptography
    private_key: Optional[str] = None  # Base64-encoded Ed25519 private key
    seal_ttl_minutes: int = 5  # Seal time-to-live

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True

    # Authentication
    jwt_secret: Optional[str] = None  # Required for production (base64 or hex string)
    jwt_expiry_hours: int = 1  # JWT token expiry (1 hour default)
    auth_required: bool = False  # Feature flag for backward compatibility

    @property
    def database_url(self) -> str:
        """Build PostgreSQL connection string."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_prefix = "RELAY_"
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This ensures settings are loaded only once and reused across requests.
    """
    return Settings()
