-- Relay Initial Schema
-- Version: 001
-- Description: Create immutable audit ledger for manifests and seals

-- Immutable audit ledger for manifests
CREATE TABLE IF NOT EXISTS manifests (
    id BIGSERIAL PRIMARY KEY,
    manifest_id UUID NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_id VARCHAR(255) NOT NULL,
    org_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    provider VARCHAR(100) NOT NULL,
    method VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL,
    reasoning TEXT NOT NULL,
    confidence_score DECIMAL(3, 2),
    environment VARCHAR(50) NOT NULL DEFAULT 'production',
    manifest_json JSONB NOT NULL
);

-- Indexes for query performance
CREATE INDEX idx_manifests_agent_id ON manifests(agent_id);
CREATE INDEX idx_manifests_org_id ON manifests(org_id);
CREATE INDEX idx_manifests_created_at ON manifests(created_at);
CREATE INDEX idx_manifests_provider ON manifests(provider);
CREATE INDEX idx_manifests_environment ON manifests(environment);

-- Seals table
CREATE TABLE IF NOT EXISTS seals (
    id BIGSERIAL PRIMARY KEY,
    seal_id VARCHAR(100) NOT NULL UNIQUE,
    manifest_id UUID NOT NULL REFERENCES manifests(manifest_id),
    approved BOOLEAN NOT NULL,
    policy_version VARCHAR(50) NOT NULL,
    denial_reason TEXT,
    signature TEXT NOT NULL,
    public_key TEXT NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    was_executed BOOLEAN DEFAULT FALSE,
    executed_at TIMESTAMPTZ
);

-- Indexes for seals
CREATE INDEX idx_seals_manifest_id ON seals(manifest_id);
CREATE INDEX idx_seals_approved ON seals(approved);
CREATE INDEX idx_seals_issued_at ON seals(issued_at);
CREATE INDEX idx_seals_seal_id ON seals(seal_id);

-- Function to prevent modifications (immutability enforcement)
CREATE OR REPLACE FUNCTION prevent_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Modification of audit records is not allowed. Table: %, Operation: %', TG_TABLE_NAME, TG_OP;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers to enforce immutability
CREATE TRIGGER immutable_manifests
BEFORE UPDATE OR DELETE ON manifests
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

CREATE TRIGGER immutable_seals
BEFORE UPDATE OR DELETE ON seals
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- Allow only updating was_executed flag on seals (exception to immutability)
CREATE OR REPLACE FUNCTION allow_execution_flag_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Only allow updating was_executed and executed_at
    IF (OLD.id = NEW.id AND
        OLD.seal_id = NEW.seal_id AND
        OLD.manifest_id = NEW.manifest_id AND
        OLD.approved = NEW.approved AND
        OLD.policy_version = NEW.policy_version AND
        OLD.denial_reason IS NOT DISTINCT FROM NEW.denial_reason AND
        OLD.signature = NEW.signature AND
        OLD.public_key = NEW.public_key AND
        OLD.issued_at = NEW.issued_at AND
        OLD.expires_at = NEW.expires_at) THEN
        RETURN NEW;
    ELSE
        RAISE EXCEPTION 'Only was_executed and executed_at fields can be updated on seals';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Drop the immutable trigger temporarily and add the execution flag trigger
DROP TRIGGER IF EXISTS immutable_seals ON seals;

CREATE TRIGGER allow_execution_update
BEFORE UPDATE ON seals
FOR EACH ROW EXECUTE FUNCTION allow_execution_flag_update();

CREATE TRIGGER prevent_seal_deletion
BEFORE DELETE ON seals
FOR EACH ROW EXECUTE FUNCTION prevent_modification();
