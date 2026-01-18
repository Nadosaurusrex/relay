"""
Organization management API endpoints.

POST /v1/orgs/register - Register a new organization (public)
GET /v1/orgs/{org_id} - Get organization details (protected)
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from gateway.db.session import get_db
from gateway.db.models import Organization, Agent
from gateway.models.auth import (
    OrganizationRegisterRequest,
    OrganizationRegisterResponse,
    OrganizationInfoResponse,
    InitialAgentInfo
)
from gateway.core.auth import (
    verify_jwt,
    generate_jwt,
    AuthContext
)
from gateway.config import get_settings


router = APIRouter(prefix="/v1/orgs", tags=["organizations"])


def generate_org_id() -> str:
    """
    Generate a unique organization ID.

    Format: org_{16_hex_chars}
    """
    random_hex = secrets.token_hex(8)
    return f"org_{random_hex}"


def generate_agent_id(org_id: str, suffix: str = "admin") -> str:
    """
    Generate an agent ID tied to an organization.

    Format: agent_{org_id}_{suffix}
    """
    return f"agent_{org_id}_{suffix}"


@router.post("/register", response_model=OrganizationRegisterResponse)
async def register_organization(
    request: OrganizationRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new organization.

    This is a public endpoint (no authentication required).
    Automatically creates an initial "admin-agent" for bootstrapping.

    Args:
        request: Organization registration details
        db: Database session

    Returns:
        OrganizationRegisterResponse with org details and initial agent credentials

    Raises:
        HTTPException: If organization creation fails
    """
    # Generate unique org_id
    org_id = generate_org_id()

    # Check if org_id already exists (collision check)
    existing_org = db.query(Organization).filter(Organization.org_id == org_id).first()
    if existing_org:
        # Extremely rare collision - retry once
        org_id = generate_org_id()

    # Create organization
    organization = Organization(
        org_id=org_id,
        org_name=request.org_name,
        contact_email=request.contact_email
    )
    db.add(organization)
    db.flush()

    # Create initial admin agent
    agent_id = generate_agent_id(org_id, "admin")

    agent = Agent(
        agent_id=agent_id,
        org_id=org_id,
        agent_name="admin-agent",
        description="Initial admin agent created during organization registration",
        api_key_hash=None  # No API keys in V1
    )
    db.add(agent)
    db.commit()

    # Generate JWT token for immediate use
    settings = get_settings()
    jwt_token = generate_jwt(agent.agent_id, organization.org_id)

    # Return response with initial agent credentials and JWT token
    return OrganizationRegisterResponse(
        org_id=organization.org_id,
        org_name=organization.org_name,
        contact_email=organization.contact_email,
        created_at=organization.created_at,
        initial_agent=InitialAgentInfo(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name
        ),
        access_token=jwt_token,
        token_type="bearer",
        expires_in=settings.jwt_expiry_hours * 3600
    )


@router.get("/{org_id}", response_model=OrganizationInfoResponse)
async def get_organization(
    org_id: str,
    auth: AuthContext = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    """
    Get organization details.

    This is a protected endpoint (requires JWT).
    Can only view details of your own organization.

    Args:
        org_id: Organization identifier
        auth: Authentication context
        db: Database session

    Returns:
        OrganizationInfoResponse with org details

    Raises:
        HTTPException: If org not found or access denied
    """
    # Authorization: can only view own org
    if org_id != auth.org_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: cannot view other organizations"
        )

    # Fetch organization
    organization = db.query(Organization).filter(Organization.org_id == org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization not found: {org_id}"
        )

    # Count agents
    agents_count = db.query(Agent).filter(Agent.org_id == org_id).count()

    return OrganizationInfoResponse(
        org_id=organization.org_id,
        org_name=organization.org_name,
        contact_email=organization.contact_email,
        agents_count=agents_count,
        created_at=organization.created_at,
        is_active=organization.is_active
    )
