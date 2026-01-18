"""
Agent management API endpoints.

POST /v1/agents/register - Register a new agent (protected)
GET /v1/agents - List organization's agents (protected)
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from gateway.db.session import get_db
from gateway.db.models import Agent
from gateway.models.auth import (
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentListResponse,
    AgentInfo
)
from gateway.core.auth import (
    verify_jwt,
    generate_jwt,
    AuthContext
)
from gateway.config import get_settings


router = APIRouter(prefix="/v1/agents", tags=["agents"])


def generate_agent_id() -> str:
    """
    Generate a unique agent ID.

    Format: agent_{16_hex_chars}
    """
    random_hex = secrets.token_hex(8)
    return f"agent_{random_hex}"


@router.post("/register", response_model=AgentRegisterResponse)
async def register_agent(
    request: AgentRegisterRequest,
    auth: AuthContext = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    """
    Register a new agent for the authenticated organization.

    This is a protected endpoint (requires JWT).
    Creates an agent tied to the authenticated org.

    Args:
        request: Agent registration details
        auth: Authentication context
        db: Database session

    Returns:
        AgentRegisterResponse with agent details and API key

    Raises:
        HTTPException: If agent creation fails
    """
    # Generate unique agent_id
    agent_id = generate_agent_id()

    # Check if agent_id already exists (collision check)
    existing_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if existing_agent:
        # Extremely rare collision - retry once
        agent_id = generate_agent_id()

    # Create agent tied to authenticated org
    agent = Agent(
        agent_id=agent_id,
        org_id=auth.org_id,
        agent_name=request.agent_name,
        description=request.description,
        api_key_hash=None  # No API keys in V1
    )
    db.add(agent)
    db.commit()

    # Generate JWT token for immediate use
    settings = get_settings()
    jwt_token = generate_jwt(agent.agent_id, agent.org_id)

    return AgentRegisterResponse(
        agent_id=agent.agent_id,
        org_id=agent.org_id,
        agent_name=agent.agent_name,
        description=agent.description,
        created_at=agent.created_at,
        access_token=jwt_token,
        token_type="bearer",
        expires_in=settings.jwt_expiry_hours * 3600
    )


@router.get("", response_model=AgentListResponse)
async def list_agents(
    auth: AuthContext = Depends(verify_jwt),
    db: Session = Depends(get_db),
):
    """
    List all agents for the authenticated organization.

    This is a protected endpoint (requires JWT).
    Returns only agents belonging to the authenticated org.

    Args:
        auth: Authentication context
        db: Database session

    Returns:
        AgentListResponse with list of agents

    Raises:
        HTTPException: If query fails
    """
    # Query agents for authenticated org
    agents = db.query(Agent).filter(Agent.org_id == auth.org_id).order_by(Agent.created_at.desc()).all()

    # Convert to response model
    agent_infos = [
        AgentInfo(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            description=agent.description,
            created_at=agent.created_at,
            is_active=agent.is_active
        )
        for agent in agents
    ]

    return AgentListResponse(
        total=len(agent_infos),
        agents=agent_infos
    )
