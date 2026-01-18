"""
Audit trail query API endpoints.

GET /v1/audit/query - Query the audit ledger
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from gateway.db.session import get_db
from gateway.core.ledger import LedgerWriter
from gateway.core.auth import verify_jwt_optional, AuthContext

router = APIRouter(prefix="/v1/audit", tags=["audit"])


@router.get("/query")
async def query_audit_trail(
    auth: Optional[AuthContext] = Depends(verify_jwt_optional),
    org_id: Optional[str] = Query(None, description="Filter by organization ID (ignored if authenticated - uses authenticated org)"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    provider: Optional[str] = Query(None, description="Filter by provider (e.g., 'stripe')"),
    approved_only: Optional[bool] = Query(None, description="Filter by approval status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """
    Query the audit trail with filters.

    This endpoint provides read-only access to the audit ledger
    for compliance, debugging, and analysis.

    If authenticated, results are automatically filtered to the authenticated organization.

    Args:
        auth: Authentication context (optional based on auth_required flag)
        org_id: Filter by organization (ignored if authenticated)
        agent_id: Filter by agent
        provider: Filter by provider
        approved_only: If True, show only approved; if False, show only denied
        limit: Maximum results to return
        offset: Pagination offset
        db: Database session

    Returns:
        List of manifest records with associated seals
    """
    ledger = LedgerWriter(db)

    # Enforce org-scoped access if authenticated
    effective_org_id = auth.org_id if auth is not None else org_id

    manifests = ledger.query_manifests(
        org_id=effective_org_id,
        agent_id=agent_id,
        provider=provider,
        approved_only=approved_only,
        limit=limit,
        offset=offset,
    )

    # Convert to response format
    results = []
    for manifest in manifests:
        # Get associated seal
        seal = manifest.seals[0] if manifest.seals else None

        results.append({
            "manifest_id": str(manifest.manifest_id),
            "created_at": manifest.created_at.isoformat(),
            "agent_id": manifest.agent_id,
            "org_id": manifest.org_id,
            "provider": manifest.provider,
            "method": manifest.method,
            "parameters": manifest.parameters,
            "reasoning": manifest.reasoning,
            "environment": manifest.environment,
            "approved": seal.approved if seal else None,
            "policy_version": seal.policy_version if seal else None,
            "denial_reason": seal.denial_reason if seal else None,
            "seal_id": seal.seal_id if seal else None,
            "was_executed": seal.was_executed if seal else None,
        })

    return {
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "results": results,
    }


@router.get("/stats")
async def get_audit_stats(
    auth: Optional[AuthContext] = Depends(verify_jwt_optional),
    org_id: Optional[str] = Query(None, description="Filter by organization ID (ignored if authenticated - uses authenticated org)"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    db: Session = Depends(get_db),
):
    """
    Get statistics about the audit trail.

    If authenticated, results are automatically filtered to the authenticated organization.

    Args:
        auth: Authentication context (optional based on auth_required flag)
        org_id: Filter by organization (ignored if authenticated)
        agent_id: Filter by agent
        db: Database session

    Returns:
        Aggregate statistics about manifests and seals
    """
    from sqlalchemy import func
    from gateway.db.models import ManifestRecord, SealRecord

    query = db.query(ManifestRecord)

    # Enforce org-scoped access if authenticated
    effective_org_id = auth.org_id if auth is not None else org_id

    if effective_org_id:
        query = query.filter(ManifestRecord.org_id == effective_org_id)
    if agent_id:
        query = query.filter(ManifestRecord.agent_id == agent_id)

    total_manifests = query.count()

    # Count approvals and denials
    approved_count = query.join(SealRecord).filter(SealRecord.approved == True).count()
    denied_count = query.join(SealRecord).filter(SealRecord.approved == False).count()

    # Count executed actions
    executed_count = query.join(SealRecord).filter(SealRecord.was_executed == True).count()

    return {
        "total_manifests": total_manifests,
        "approved": approved_count,
        "denied": denied_count,
        "executed": executed_count,
        "approval_rate": round(approved_count / total_manifests * 100, 2) if total_manifests > 0 else 0,
    }
