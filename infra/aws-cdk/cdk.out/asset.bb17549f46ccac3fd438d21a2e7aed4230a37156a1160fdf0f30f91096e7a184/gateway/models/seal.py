"""
Seal data models for Relay.

A Seal is a cryptographic proof that an action was approved by the policy engine.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Seal(BaseModel):
    """
    A Seal is a cryptographic proof of policy approval.

    It contains an Ed25519 signature over the manifest data,
    proving that the action was validated against deterministic policies.
    """

    seal_id: str = Field(..., description="Unique identifier for this seal")
    manifest_id: UUID = Field(..., description="The manifest this seal approves")
    approved: bool = Field(..., description="Whether the action was approved")
    policy_version: str = Field(..., description="Version of policies that were evaluated")
    denial_reason: Optional[str] = Field(None, description="Reason for denial if not approved")

    signature: str = Field(..., description="Base64-encoded Ed25519 signature")
    public_key: str = Field(..., description="Base64-encoded Ed25519 public key for verification")

    issued_at: datetime = Field(default_factory=datetime.utcnow, description="When this seal was issued")
    expires_at: datetime = Field(..., description="When this seal expires (5-minute TTL)")

    was_executed: bool = Field(default=False, description="Whether the sealed action was executed")
    executed_at: Optional[datetime] = Field(None, description="When the action was executed")

    @classmethod
    def generate_seal_id(cls, manifest_id: UUID) -> str:
        """
        Generate a unique seal ID.

        Format: seal_{timestamp}_{manifest_id_prefix}
        """
        timestamp = int(datetime.utcnow().timestamp())
        manifest_prefix = str(manifest_id).split('-')[0]
        return f"seal_{timestamp}_{manifest_prefix}"

    @classmethod
    def create_expiry(cls, ttl_minutes: int = 5) -> datetime:
        """
        Create an expiry timestamp.

        Default TTL is 5 minutes to prevent replay attacks.
        """
        return datetime.utcnow() + timedelta(minutes=ttl_minutes)

    def is_expired(self) -> bool:
        """Check if this seal has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """
        Check if this seal is valid for use.

        A seal is valid if:
        1. It was approved
        2. It hasn't expired
        3. It hasn't been executed yet (one-time use)
        """
        return self.approved and not self.is_expired() and not self.was_executed

    class Config:
        json_schema_extra = {
            "example": {
                "seal_id": "seal_1705491000_550e8400",
                "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
                "approved": True,
                "policy_version": "v1.2.3",
                "denial_reason": None,
                "signature": "kZXJ0aWZpY2F0ZSBmb3IgdGVzdGluZyBwdXJwb3Nlcy4=",
                "public_key": "MCowBQYDK2VwAyEA1234567890abcdef",
                "issued_at": "2026-01-17T10:30:05Z",
                "expires_at": "2026-01-17T10:35:05Z",
                "was_executed": False,
                "executed_at": None
            }
        }


class SealVerificationRequest(BaseModel):
    """Request to verify a seal's authenticity."""

    seal_id: str = Field(..., description="The seal ID to verify")
    signature: str = Field(..., description="The signature to verify")
    manifest_id: Optional[UUID] = Field(None, description="Optional manifest ID for additional validation")


class SealVerificationResponse(BaseModel):
    """Response from seal verification."""

    seal_id: str = Field(..., description="The seal ID that was verified")
    valid: bool = Field(..., description="Whether the seal is valid")
    approved: bool = Field(..., description="Whether the underlying action was approved")
    expired: bool = Field(..., description="Whether the seal has expired")
    already_executed: bool = Field(..., description="Whether the seal has already been used")
    reason: Optional[str] = Field(None, description="Reason if seal is invalid")
    manifest_id: Optional[UUID] = Field(None, description="The manifest this seal approves")
