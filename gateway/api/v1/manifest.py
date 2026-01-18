"""
Manifest validation API endpoints.

POST /v1/manifest/validate - Validate a manifest against policies
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from gateway.db.session import get_db
from gateway.models.manifest import ManifestValidationRequest, ManifestValidationResponse
from gateway.core.seal import SealGenerator
from gateway.core.policy_engine import PolicyEngine, PolicyEngineError
from gateway.core.ledger import LedgerWriter
from gateway.core.auth import verify_jwt_optional, AuthContext, log_auth_event
from gateway.config import get_settings

router = APIRouter(prefix="/v1/manifest", tags=["manifest"])


@router.post("/validate", response_model=ManifestValidationResponse)
async def validate_manifest(
    req: Request,
    request: ManifestValidationRequest,
    auth: Optional[AuthContext] = Depends(verify_jwt_optional),
    db: Session = Depends(get_db),
):
    """
    Validate a manifest against policies.

    This is the core endpoint of Relay:
    1. Validates manifest schema (already done by Pydantic)
    2. Calls OPA policy engine for decision
    3. Generates cryptographic seal (Ed25519)
    4. Writes to immutable audit ledger
    5. Returns sealed approval or denial

    Args:
        req: FastAPI request object
        request: ManifestValidationRequest with manifest to validate
        auth: Authentication context (optional based on auth_required flag)
        db: Database session

    Returns:
        ManifestValidationResponse with seal or denial reason

    Raises:
        HTTPException: If policy engine is unavailable or ledger write fails
    """
    manifest = request.manifest
    settings = get_settings()

    # Authorization check: if authenticated, manifest org_id must match
    if auth is not None:
        if manifest.agent.org_id != auth.org_id:
            await log_auth_event(
                db=db,
                event_type="authorization_failure",
                success=False,
                agent_id=auth.agent_id,
                org_id=auth.org_id,
                endpoint="/v1/manifest/validate",
                ip_address=req.client.host if req.client else None,
                failure_reason=f"Org mismatch: authenticated as {auth.org_id}, manifest has {manifest.agent.org_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="Organization mismatch: cannot validate manifest for another organization"
            )

    # Initialize components
    policy_engine = PolicyEngine(
        opa_url=settings.opa_url,
        policy_path=settings.policy_path,
    )
    seal_generator = SealGenerator(settings.private_key)
    ledger = LedgerWriter(db)

    try:
        # Step 1: Evaluate against OPA policies
        approved, denial_reason = policy_engine.evaluate(manifest)
        policy_version = policy_engine.get_policy_version()

        # Step 2: Generate cryptographic seal
        seal = seal_generator.create_seal(
            manifest=manifest,
            approved=approved,
            policy_version=policy_version,
            denial_reason=denial_reason,
            ttl_minutes=settings.seal_ttl_minutes,
        )

        # Step 3: Write to audit ledger (if not dry run)
        if not request.dry_run:
            ledger.write_manifest(manifest)
            ledger.write_seal(seal)
            db.commit()

        # Step 4: Return response
        return ManifestValidationResponse(
            manifest_id=manifest.manifest_id,
            approved=approved,
            seal=seal if approved else None,
            denial_reason=denial_reason,
            policy_version=policy_version,
        )

    except PolicyEngineError as e:
        # Policy engine unavailable - fail closed
        raise HTTPException(
            status_code=503,
            detail=f"Policy engine unavailable: {str(e)}"
        )
    except Exception as e:
        # Unexpected error - fail closed
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Manifest validation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status of the manifest validation service
    """
    settings = get_settings()
    policy_engine = PolicyEngine(opa_url=settings.opa_url)

    opa_healthy = policy_engine.health_check()

    return {
        "status": "healthy" if opa_healthy else "degraded",
        "opa_available": opa_healthy,
        "policy_version": policy_engine.get_policy_version() if opa_healthy else "unknown",
    }
