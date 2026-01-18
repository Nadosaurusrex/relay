"""
Authentication and authorization data models for Relay.

These models define the request/response schemas for auth endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ========== Organization Models ==========

class OrganizationRegisterRequest(BaseModel):
    """Request model for registering a new organization."""

    org_name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    contact_email: str = Field(..., min_length=3, max_length=255, description="Contact email for the organization")

    @field_validator('org_name')
    @classmethod
    def validate_org_name(cls, v: str) -> str:
        """Ensure org name is not just whitespace."""
        if not v.strip():
            raise ValueError("Organization name cannot be empty")
        return v.strip()


class InitialAgentInfo(BaseModel):
    """Information about the initial admin agent created during org registration."""

    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")


class OrganizationRegisterResponse(BaseModel):
    """Response model for organization registration."""

    org_id: str = Field(..., description="Organization identifier")
    org_name: str = Field(..., description="Organization name")
    contact_email: str = Field(..., description="Contact email")
    created_at: datetime = Field(..., description="When the organization was created")
    initial_agent: InitialAgentInfo = Field(..., description="Initial admin agent credentials")
    access_token: str = Field(..., description="JWT access token for immediate use")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "org_id": "org_abc123",
                "org_name": "Acme Corp",
                "contact_email": "admin@acme.com",
                "created_at": "2026-01-18T10:00:00Z",
                "initial_agent": {
                    "agent_id": "agent_org_abc123_admin",
                    "agent_name": "admin-agent"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class OrganizationInfoResponse(BaseModel):
    """Response model for organization information."""

    org_id: str = Field(..., description="Organization identifier")
    org_name: str = Field(..., description="Organization name")
    contact_email: str = Field(..., description="Contact email")
    agents_count: int = Field(..., description="Number of agents in the organization")
    created_at: datetime = Field(..., description="When the organization was created")
    is_active: bool = Field(..., description="Whether the organization is active")

    class Config:
        json_schema_extra = {
            "example": {
                "org_id": "org_abc123",
                "org_name": "Acme Corp",
                "contact_email": "admin@acme.com",
                "agents_count": 3,
                "created_at": "2026-01-18T10:00:00Z",
                "is_active": True
            }
        }


# ========== Agent Models ==========

class AgentRegisterRequest(BaseModel):
    """Request model for registering a new agent."""

    agent_name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    description: Optional[str] = Field(None, max_length=1000, description="Agent description")

    @field_validator('agent_name')
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """Ensure agent name is not just whitespace."""
        if not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v.strip()


class AgentRegisterResponse(BaseModel):
    """Response model for agent registration."""

    agent_id: str = Field(..., description="Agent identifier")
    org_id: str = Field(..., description="Organization identifier")
    agent_name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    created_at: datetime = Field(..., description="When the agent was created")
    access_token: str = Field(..., description="JWT access token for immediate use")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_id": "agent_xyz789",
                "org_id": "org_abc123",
                "agent_name": "sales-bot",
                "description": "Handles quote approvals",
                "created_at": "2026-01-18T10:05:00Z",
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class AgentInfo(BaseModel):
    """Information about an agent."""

    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    created_at: datetime = Field(..., description="When the agent was created")
    is_active: bool = Field(..., description="Whether the agent is active")


class AgentListResponse(BaseModel):
    """Response model for listing agents."""

    total: int = Field(..., description="Total number of agents")
    agents: list[AgentInfo] = Field(..., description="List of agents")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 3,
                "agents": [
                    {
                        "agent_id": "agent_xyz789",
                        "agent_name": "sales-bot",
                        "description": "Handles quote approvals",
                        "created_at": "2026-01-18T10:05:00Z",
                        "is_active": True
                    }
                ]
            }
        }


# ========== Auth Event Models ==========

class AuthEventInfo(BaseModel):
    """Information about an authentication/authorization event."""

    event_id: UUID = Field(..., description="Event identifier")
    event_type: str = Field(..., description="Type of auth event")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    org_id: Optional[str] = Field(None, description="Organization identifier")
    endpoint: Optional[str] = Field(None, description="API endpoint")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    success: bool = Field(..., description="Whether the event was successful")
    failure_reason: Optional[str] = Field(None, description="Reason for failure")
    created_at: datetime = Field(..., description="When the event occurred")


class AuthEventListResponse(BaseModel):
    """Response model for listing auth events."""

    total: int = Field(..., description="Total number of events")
    events: list[AuthEventInfo] = Field(..., description="List of auth events")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 5,
                "events": [
                    {
                        "event_id": "550e8400-e29b-41d4-a716-446655440000",
                        "event_type": "authentication",
                        "agent_id": "agent_xyz789",
                        "org_id": "org_abc123",
                        "endpoint": "/v1/auth/token",
                        "ip_address": "192.168.1.1",
                        "success": True,
                        "failure_reason": None,
                        "created_at": "2026-01-18T10:00:00Z"
                    }
                ]
            }
        }
