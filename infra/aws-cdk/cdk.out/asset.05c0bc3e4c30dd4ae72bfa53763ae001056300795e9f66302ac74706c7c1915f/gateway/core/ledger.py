"""
Audit ledger writer for Relay.

Writes manifests and seals to the immutable PostgreSQL audit trail.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from gateway.db.models import ManifestRecord, SealRecord
from gateway.models.manifest import Manifest
from gateway.models.seal import Seal


class LedgerWriter:
    """
    Writes audit records to the immutable ledger.

    All writes are append-only. No updates or deletes are allowed
    (enforced by database triggers).
    """

    def __init__(self, session: Session):
        self.session = session

    def write_manifest(self, manifest: Manifest) -> ManifestRecord:
        """
        Write a manifest to the audit ledger.

        Args:
            manifest: The manifest to write

        Returns:
            The created ManifestRecord

        Raises:
            IntegrityError: If manifest_id already exists
        """
        record = ManifestRecord(
            manifest_id=manifest.manifest_id,
            created_at=manifest.timestamp,
            agent_id=manifest.agent.agent_id,
            org_id=manifest.agent.org_id,
            user_id=manifest.agent.user_id,
            provider=manifest.action.provider,
            method=manifest.action.method,
            parameters=manifest.action.parameters,
            reasoning=manifest.justification.reasoning,
            confidence_score=manifest.justification.confidence_score,
            environment=manifest.environment,
            manifest_json=manifest.model_dump(mode='json'),
        )

        self.session.add(record)
        self.session.flush()  # Get the ID without committing

        return record

    def write_seal(self, seal: Seal) -> SealRecord:
        """
        Write a seal to the audit ledger.

        Args:
            seal: The seal to write

        Returns:
            The created SealRecord

        Raises:
            IntegrityError: If seal_id already exists or manifest_id doesn't exist
        """
        record = SealRecord(
            seal_id=seal.seal_id,
            manifest_id=seal.manifest_id,
            approved=seal.approved,
            policy_version=seal.policy_version,
            denial_reason=seal.denial_reason,
            signature=seal.signature,
            public_key=seal.public_key,
            issued_at=seal.issued_at,
            expires_at=seal.expires_at,
            was_executed=seal.was_executed,
            executed_at=seal.executed_at,
        )

        self.session.add(record)
        self.session.flush()

        return record

    def get_manifest(self, manifest_id: UUID) -> Optional[ManifestRecord]:
        """
        Retrieve a manifest by ID.

        Args:
            manifest_id: The manifest ID to retrieve

        Returns:
            ManifestRecord if found, None otherwise
        """
        return self.session.query(ManifestRecord).filter(
            ManifestRecord.manifest_id == manifest_id
        ).first()

    def get_seal(self, seal_id: str) -> Optional[SealRecord]:
        """
        Retrieve a seal by ID.

        Args:
            seal_id: The seal ID to retrieve

        Returns:
            SealRecord if found, None otherwise
        """
        return self.session.query(SealRecord).filter(
            SealRecord.seal_id == seal_id
        ).first()

    def mark_seal_executed(self, seal_id: str) -> bool:
        """
        Mark a seal as executed.

        This is the ONLY update operation allowed on the seals table.

        Args:
            seal_id: The seal to mark as executed

        Returns:
            True if updated, False if seal not found

        Raises:
            Exception: If the seal was already executed
        """
        seal = self.get_seal(seal_id)
        if not seal:
            return False

        if seal.was_executed:
            raise Exception(f"Seal {seal_id} was already executed at {seal.executed_at}")

        seal.was_executed = True
        seal.executed_at = datetime.utcnow()
        self.session.flush()

        return True

    def query_manifests(
        self,
        org_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        provider: Optional[str] = None,
        approved_only: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ManifestRecord]:
        """
        Query manifests with filters.

        Args:
            org_id: Filter by organization
            agent_id: Filter by agent
            provider: Filter by provider
            approved_only: If True, only show approved actions; if False, only denied
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of ManifestRecords matching the filters
        """
        query = self.session.query(ManifestRecord)

        if org_id:
            query = query.filter(ManifestRecord.org_id == org_id)
        if agent_id:
            query = query.filter(ManifestRecord.agent_id == agent_id)
        if provider:
            query = query.filter(ManifestRecord.provider == provider)

        # Join with seals if filtering by approval status
        if approved_only is not None:
            query = query.join(SealRecord).filter(
                SealRecord.approved == approved_only
            )

        # Order by most recent first
        query = query.order_by(ManifestRecord.created_at.desc())

        return query.limit(limit).offset(offset).all()


class LedgerError(Exception):
    """Raised when ledger operations fail."""

    pass
