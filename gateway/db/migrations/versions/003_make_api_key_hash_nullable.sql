-- Migration: Make api_key_hash nullable
-- Version: 003
-- Description: Remove API key requirement from agents table for V1 simplification

-- Make api_key_hash nullable
ALTER TABLE agents
ALTER COLUMN api_key_hash DROP NOT NULL;

-- Comment to explain the change
COMMENT ON COLUMN agents.api_key_hash IS 'API key hash (nullable in V1 - agents use JWT-only authentication)';
