"""
Seal verification API endpoints.

GET /v1/seal/verify - Verify seal authenticity
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from gateway.db.session import get_db
from gateway.models.seal import SealVerificationRequest, SealVerificationResponse
from gateway.core.seal import SealGenerator
from gateway.core.ledger import LedgerWriter
from gateway.config import get_settings

router = APIRouter(prefix="/v1/seal", tags=["seal"])


@router.get("/verify", response_model=SealVerificationResponse)
async def verify_seal(
    seal_id: str = Query(..., description="The seal ID to verify"),
    db: Session = Depends(get_db),
):
    """
    Verify a seal's authenticity.

    This endpoint allows target services to verify that a seal is:
    1. Authentic (valid cryptographic signature)
    2. Not expired
    3. Not already executed (one-time use)

    Args:
        seal_id: The seal ID to verify
        db: Database session

    Returns:
        SealVerificationResponse with validation results

    Raises:
        HTTPException: If seal not found
    """
    settings = get_settings()
    ledger = LedgerWriter(db)
    seal_generator = SealGenerator(settings.private_key)

    # Retrieve seal from ledger
    seal_record = ledger.get_seal(seal_id)
    if not seal_record:
        raise HTTPException(
            status_code=404,
            detail=f"Seal not found: {seal_id}"
        )

    # Retrieve associated manifest
    manifest_record = ledger.get_manifest(seal_record.manifest_id)
    if not manifest_record:
        raise HTTPException(
            status_code=404,
            detail=f"Manifest not found for seal: {seal_id}"
        )

    # Convert records to Pydantic models for verification
    from gateway.models.manifest import Manifest
    from gateway.models.seal import Seal

    manifest = Manifest(**manifest_record.manifest_json)
    seal = Seal(
        seal_id=seal_record.seal_id,
        manifest_id=seal_record.manifest_id,
        approved=seal_record.approved,
        policy_version=seal_record.policy_version,
        denial_reason=seal_record.denial_reason,
        signature=seal_record.signature,
        public_key=seal_record.public_key,
        issued_at=seal_record.issued_at,
        expires_at=seal_record.expires_at,
        was_executed=seal_record.was_executed,
        executed_at=seal_record.executed_at,
    )

    # Verify cryptographic signature
    signature_valid = seal_generator.verify_seal(seal, manifest)

    # Check expiry
    expired = seal.is_expired()

    # Check if already executed
    already_executed = seal.was_executed

    # Determine overall validity
    valid = signature_valid and not expired and not already_executed and seal.approved

    # Build reason if invalid
    reason = None
    if not signature_valid:
        reason = "Invalid cryptographic signature"
    elif not seal.approved:
        reason = f"Action was denied: {seal.denial_reason}"
    elif expired:
        reason = "Seal has expired"
    elif already_executed:
        reason = "Seal has already been executed"

    return SealVerificationResponse(
        seal_id=seal_id,
        valid=valid,
        approved=seal.approved,
        expired=expired,
        already_executed=already_executed,
        reason=reason,
        manifest_id=seal.manifest_id,
    )


@router.post("/mark-executed")
async def mark_seal_executed(
    seal_id: str = Query(..., description="The seal ID to mark as executed"),
    db: Session = Depends(get_db),
):
    """
    Mark a seal as executed.

    This should be called by the agent after successfully executing the action.
    It prevents the seal from being reused (replay attack prevention).

    Args:
        seal_id: The seal ID to mark as executed
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If seal not found or already executed
    """
    ledger = LedgerWriter(db)

    try:
        success = ledger.mark_seal_executed(seal_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Seal not found: {seal_id}"
            )

        db.commit()

        return {
            "status": "success",
            "message": f"Seal {seal_id} marked as executed",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
