-- Relay Auth System Schema
-- Version: 002
-- Description: Add organizations, agents, and auth_events tables for V1 authentication

-- Organizations table - registry of all organizations
CREATE TABLE IF NOT EXISTS organizations (
    id BIGSERIAL PRIMARY KEY,
    org_id VARCHAR(255) NOT NULL UNIQUE,
    org_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Indexes for organizations
CREATE INDEX idx_organizations_org_id ON organizations(org_id);
CREATE INDEX idx_organizations_created_at ON organizations(created_at);

-- Agents table - agent registry with API keys
CREATE TABLE IF NOT EXISTS agents (
    id BIGSERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL UNIQUE,
    org_id VARCHAR(255) NOT NULL REFERENCES organizations(org_id),
    agent_name VARCHAR(255) NOT NULL,
    description TEXT,
    api_key_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Indexes for agents
CREATE INDEX idx_agents_agent_id ON agents(agent_id);
CREATE INDEX idx_agents_org_id ON agents(org_id);
CREATE INDEX idx_agents_created_at ON agents(created_at);

-- Auth events table - immutable authentication/authorization audit trail
CREATE TABLE IF NOT EXISTS auth_events (
    id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    agent_id VARCHAR(255),
    org_id VARCHAR(255),
    endpoint VARCHAR(255),
    ip_address VARCHAR(45),
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for auth_events
CREATE INDEX idx_auth_events_agent_id ON auth_events(agent_id);
CREATE INDEX idx_auth_events_org_id ON auth_events(org_id);
CREATE INDEX idx_auth_events_created_at ON auth_events(created_at);
CREATE INDEX idx_auth_events_event_type ON auth_events(event_type);
CREATE INDEX idx_auth_events_success ON auth_events(success);

-- Immutability trigger for auth_events
CREATE TRIGGER immutable_auth_events
BEFORE UPDATE OR DELETE ON auth_events
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- Note: prevent_modification() function already exists from 001_initial_schema.sql
