-- Database: PostgreSQL
-- OMNI Enterprise Model Registry

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS ml_model_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    framework VARCHAR(50) NOT NULL, -- e.g., 'pytorch', 'tensorflow', 'onnx'
    artifact_uri VARCHAR(1024) NOT NULL,
    signature JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'STAGING' CHECK (status IN ('STAGING', 'PRODUCTION', 'ARCHIVED', 'FAILED')),
    metrics JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (model_name, version)
);

CREATE INDEX idx_model_status ON ml_model_registry(status);
CREATE INDEX idx_model_name ON ml_model_registry(model_name);

-- Create history tracking table
CREATE TABLE IF NOT EXISTS ml_model_transitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_model_registry(id) ON DELETE CASCADE,
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    transitioned_by VARCHAR(255),
    reason TEXT,
    transitioned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to automatically track status transitions
CREATE OR REPLACE FUNCTION track_model_transition()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO ml_model_transitions (model_id, previous_status, new_status)
        VALUES (NEW.id, OLD.status, NEW.status);
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS model_transition_trigger ON ml_model_registry;
CREATE TRIGGER model_transition_trigger
BEFORE UPDATE ON ml_model_registry
FOR EACH ROW
EXECUTE PROCEDURE track_model_transition();
