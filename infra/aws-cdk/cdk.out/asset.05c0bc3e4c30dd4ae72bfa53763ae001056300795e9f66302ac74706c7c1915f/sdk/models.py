"""
Data models for Relay SDK.

Simplified versions of Gateway models for agent use.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Agent identity and context."""

    agent_id: str
    org_id: str
    user_id: Optional[str] = None


class ActionRequest(BaseModel):
    """Action being requested."""

    provider: str
    method: str
    parameters: Dict[str, Any]


class Justification(BaseModel):
    """Agent's reasoning for the action."""

    reasoning: str
    confidence_score: Optional[float] = None
    context: Optional[Dict[str, Any]] = None


class Manifest(BaseModel):
    """
    Manifest describing an agent action request.
    """

    manifest_id: UUID = Field(default_factory=uuid4)
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: AgentContext
    action: ActionRequest
    justification: Justification
    environment: str = "production"


class Seal(BaseModel):
    """
    Cryptographic seal proving policy approval.
    """

    seal_id: str
    manifest_id: UUID
    approved: bool
    policy_version: str
    denial_reason: Optional[str] = None
    signature: str
    public_key: str
    issued_at: datetime
    expires_at: datetime
    was_executed: bool = False
    executed_at: Optional[datetime] = None


class PolicyViolationError(Exception):
    """
    Raised when an action is denied by policy.
    """

    def __init__(self, denial_reason: str, manifest_id: UUID):
        self.denial_reason = denial_reason
        self.manifest_id = manifest_id
        super().__init__(f"Policy violation: {denial_reason}")
