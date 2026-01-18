"""
Manifest data models for Relay.

A Manifest is the core primitive that describes an agent action request.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class AgentContext(BaseModel):
    """Agent identity and context information."""

    agent_id: str = Field(..., description="Unique identifier for the agent")
    org_id: str = Field(..., description="Organization identifier")
    user_id: Optional[str] = Field(None, description="User on whose behalf the agent acts")


class ActionRequest(BaseModel):
    """The action being requested by the agent."""

    provider: str = Field(..., description="Service provider (e.g., 'stripe', 'aws', 'github')")
    method: str = Field(..., description="Method or operation (e.g., 'create_payment', 'delete_bucket')")
    parameters: Dict[str, Any] = Field(..., description="Action parameters as key-value pairs")

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Ensure provider is lowercase and alphanumeric."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Provider must be alphanumeric (underscores and hyphens allowed)")
        return v.lower()

    @field_validator('method')
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Ensure method is lowercase and alphanumeric."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Method must be alphanumeric (underscores and hyphens allowed)")
        return v.lower()


class Justification(BaseModel):
    """Agent's reasoning for the action."""

    reasoning: str = Field(..., description="Natural language explanation of why this action is needed")
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Agent's confidence in this action (0.0 to 1.0)"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context data")


class Manifest(BaseModel):
    """
    The Manifest is the core primitive of Relay.

    It describes an agent action request with full context,
    enabling deterministic policy evaluation.
    """

    manifest_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this manifest")
    version: str = Field(default="1.0", description="Manifest schema version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this manifest was created")

    agent: AgentContext = Field(..., description="Agent identity and context")
    action: ActionRequest = Field(..., description="The action being requested")
    justification: Justification = Field(..., description="Agent's reasoning for the action")

    environment: str = Field(
        default="production",
        description="Deployment environment (e.g., 'production', 'staging', 'development')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": "1.0",
                "timestamp": "2026-01-17T10:30:00Z",
                "agent": {
                    "agent_id": "sales-agent-001",
                    "org_id": "acme-corp",
                    "user_id": "user@acme.com"
                },
                "action": {
                    "provider": "stripe",
                    "method": "create_payment",
                    "parameters": {
                        "amount": 4500,
                        "currency": "USD",
                        "customer_id": "cus_123"
                    }
                },
                "justification": {
                    "reasoning": "Customer approved quote Q-2026-001 for $45.00",
                    "confidence_score": 0.95
                },
                "environment": "production"
            }
        }

    def to_policy_input(self) -> Dict[str, Any]:
        """
        Convert manifest to OPA policy input format.

        Returns a dictionary suitable for OPA evaluation.
        """
        return {
            "manifest_id": str(self.manifest_id),
            "timestamp": self.timestamp.isoformat(),
            "agent": self.agent.model_dump(),
            "action": self.action.model_dump(),
            "justification": self.justification.model_dump(),
            "environment": self.environment
        }


class ManifestValidationRequest(BaseModel):
    """Request to validate a manifest against policies."""

    manifest: Manifest = Field(..., description="The manifest to validate")
    dry_run: bool = Field(
        default=False,
        description="If true, validate without creating audit records"
    )


class ManifestValidationResponse(BaseModel):
    """Response from manifest validation."""

    manifest_id: UUID = Field(..., description="The manifest ID that was validated")
    approved: bool = Field(..., description="Whether the action was approved")
    seal: Optional["Seal"] = Field(None, description="Cryptographic seal if approved")
    denial_reason: Optional[str] = Field(None, description="Reason for denial if not approved")
    policy_version: str = Field(..., description="Version of policies that were evaluated")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When validation occurred")


# Import Seal model to resolve forward reference
from .seal import Seal  # noqa: E402

ManifestValidationResponse.model_rebuild()
