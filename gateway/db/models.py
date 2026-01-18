"""
SQLAlchemy ORM models for Relay audit ledger.
"""

from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, DateTime,
    DECIMAL, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from gateway.db.session import Base


class ManifestRecord(Base):
    """
    Immutable record of an agent action request.

    This table serves as the audit trail for all agent actions.
    """

    __tablename__ = "manifests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    manifest_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # Agent context
    agent_id = Column(String(255), nullable=False, index=True)
    org_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True)

    # Action details
    provider = Column(String(100), nullable=False, index=True)
    method = Column(String(100), nullable=False)
    parameters = Column(JSONB, nullable=False)

    # Justification
    reasoning = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(3, 2), nullable=True)

    # Environment
    environment = Column(String(50), nullable=False, default="production", index=True)

    # Full manifest JSON for complete audit trail
    manifest_json = Column(JSONB, nullable=False)

    # Relationship to seals
    seals = relationship("SealRecord", back_populates="manifest")

    def __repr__(self):
        return f"<ManifestRecord(id={self.id}, manifest_id={self.manifest_id}, agent={self.agent_id})>"


class SealRecord(Base):
    """
    Cryptographic seal proving policy approval/denial.

    This table is also immutable except for execution tracking.
    """

    __tablename__ = "seals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    seal_id = Column(String(100), nullable=False, unique=True, index=True)
    manifest_id = Column(UUID(as_uuid=True), ForeignKey("manifests.manifest_id"), nullable=False, index=True)

    # Policy decision
    approved = Column(Boolean, nullable=False, index=True)
    policy_version = Column(String(50), nullable=False)
    denial_reason = Column(Text, nullable=True)

    # Cryptographic proof
    signature = Column(Text, nullable=False)
    public_key = Column(Text, nullable=False)

    # Timestamps
    issued_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Execution tracking (only fields that can be updated)
    was_executed = Column(Boolean, default=False)
    executed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to manifest
    manifest = relationship("ManifestRecord", back_populates="seals")

    def __repr__(self):
        return f"<SealRecord(seal_id={self.seal_id}, approved={self.approved})>"


# Create indexes for common query patterns
Index("idx_manifests_org_agent", ManifestRecord.org_id, ManifestRecord.agent_id)
Index("idx_manifests_provider_method", ManifestRecord.provider, ManifestRecord.method)
Index("idx_seals_approved_issued", SealRecord.approved, SealRecord.issued_at)


class Organization(Base):
    """
    Organization registry for multi-tenancy.

    Each organization can have multiple agents.
    """

    __tablename__ = "organizations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    org_id = Column(String(255), nullable=False, unique=True, index=True)
    org_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationship to agents
    agents = relationship("Agent", back_populates="organization")

    def __repr__(self):
        return f"<Organization(org_id={self.org_id}, org_name={self.org_name})>"


class Agent(Base):
    """
    Agent registry with JWT-only authentication.

    Each agent belongs to one organization and receives a JWT token upon registration.
    api_key_hash is nullable in V1 (reserved for future use).
    """

    __tablename__ = "agents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_id = Column(String(255), nullable=False, unique=True, index=True)
    org_id = Column(String(255), ForeignKey("organizations.org_id"), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    api_key_hash = Column(String(255), nullable=True)  # Nullable in V1
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationship to organization
    organization = relationship("Organization", back_populates="agents")

    def __repr__(self):
        return f"<Agent(agent_id={self.agent_id}, org_id={self.org_id})>"


class AuthEvent(Base):
    """
    Immutable audit trail for authentication and authorization events.

    This table logs all auth-related events for security auditing.
    """

    __tablename__ = "auth_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    agent_id = Column(String(255), nullable=True)
    org_id = Column(String(255), nullable=True)
    endpoint = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuthEvent(event_type={self.event_type}, success={self.success}, agent={self.agent_id})>"


# Indexes for auth tables
Index("idx_agents_org_active", Agent.org_id, Agent.is_active)
Index("idx_auth_events_type_success", AuthEvent.event_type, AuthEvent.success)
