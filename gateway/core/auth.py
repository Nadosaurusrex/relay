"""
Authentication and authorization utilities for Relay Gateway.

Provides JWT token generation/verification for V1 simplified auth.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from gateway.config import get_settings
from gateway.db.models import Agent, AuthEvent
from gateway.db.session import get_db


class AuthContext:
    """
    Authentication context containing authenticated agent and org information.

    This is injected into protected endpoints via dependency injection.
    """

    def __init__(self, agent_id: str, org_id: str):
        self.agent_id = agent_id
        self.org_id = org_id

    def __repr__(self):
        return f"<AuthContext(agent_id={self.agent_id}, org_id={self.org_id})>"


# HTTP Bearer token scheme for FastAPI
security = HTTPBearer(auto_error=False)


def generate_jwt(agent_id: str, org_id: str) -> str:
    """
    Generate a JWT token for an authenticated agent.

    Args:
        agent_id: Agent identifier
        org_id: Organization identifier

    Returns:
        str: JWT token
    """
    settings = get_settings()

    if not settings.jwt_secret:
        raise ValueError("JWT secret not configured")

    now = datetime.utcnow()
    expiry = now + timedelta(hours=settings.jwt_expiry_hours)

    payload = {
        "agent_id": agent_id,
        "org_id": org_id,
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp())
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token


def decode_jwt(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        dict: Decoded token payload

    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    settings = get_settings()

    if not settings.jwt_secret:
        raise ValueError("JWT secret not configured")

    # Add leeway to handle clock skew
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        leeway=10  # Allow 10 seconds of clock skew
    )
    return payload


async def log_auth_event(
    db: Session,
    event_type: str,
    success: bool,
    agent_id: Optional[str] = None,
    org_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    ip_address: Optional[str] = None,
    failure_reason: Optional[str] = None
):
    """
    Log an authentication or authorization event to the audit trail.

    Args:
        db: Database session
        event_type: Type of auth event (authentication, authorization_success, authorization_failure)
        success: Whether the event was successful
        agent_id: Agent identifier (optional)
        org_id: Organization identifier (optional)
        endpoint: API endpoint being accessed (optional)
        ip_address: Client IP address (optional)
        failure_reason: Reason for failure (optional)
    """
    event = AuthEvent(
        event_id=uuid4(),
        event_type=event_type,
        agent_id=agent_id,
        org_id=org_id,
        endpoint=endpoint,
        ip_address=ip_address,
        success=success,
        failure_reason=failure_reason
    )
    db.add(event)
    db.commit()


async def verify_jwt_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[AuthContext]:
    """
    Optional JWT verification for backward compatibility.

    This dependency checks if auth is required via feature flag.
    If auth_required=false, allows access without token.
    If auth_required=true, enforces JWT verification.

    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        Optional[AuthContext]: Auth context if authenticated, None if auth not required

    Raises:
        HTTPException: If auth is required and token is invalid
    """
    settings = get_settings()

    # Feature flag: allow access without auth if not required
    if not settings.auth_required:
        return None

    # If auth is required, token must be present
    if not credentials:
        await log_auth_event(
            db=db,
            event_type="authorization_failure",
            success=False,
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None,
            failure_reason="Missing authorization token"
        )
        raise HTTPException(
            status_code=401,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await verify_jwt(request, credentials, db)


async def verify_jwt(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AuthContext:
    """
    FastAPI dependency for JWT verification.

    This enforces authentication and returns the auth context.

    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        AuthContext: Authenticated agent and org information

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        await log_auth_event(
            db=db,
            event_type="authorization_failure",
            success=False,
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None,
            failure_reason="Missing authorization token"
        )
        raise HTTPException(
            status_code=401,
            detail="Authorization token required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    try:
        payload = decode_jwt(token)
        agent_id = payload.get("agent_id")
        org_id = payload.get("org_id")

        if not agent_id or not org_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Verify agent exists and is active
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent or not agent.is_active:
            await log_auth_event(
                db=db,
                event_type="authorization_failure",
                success=False,
                agent_id=agent_id,
                org_id=org_id,
                endpoint=str(request.url.path),
                ip_address=request.client.host if request.client else None,
                failure_reason="Agent not found or inactive"
            )
            raise HTTPException(status_code=401, detail="Agent not found or inactive")

        # Log successful authorization
        await log_auth_event(
            db=db,
            event_type="authorization_success",
            success=True,
            agent_id=agent_id,
            org_id=org_id,
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None
        )

        return AuthContext(agent_id=agent_id, org_id=org_id)

    except jwt.ExpiredSignatureError:
        await log_auth_event(
            db=db,
            event_type="authorization_failure",
            success=False,
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None,
            failure_reason="Token expired"
        )
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        await log_auth_event(
            db=db,
            event_type="authorization_failure",
            success=False,
            endpoint=str(request.url.path),
            ip_address=request.client.host if request.client else None,
            failure_reason=f"Invalid token: {str(e)}"
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
