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
