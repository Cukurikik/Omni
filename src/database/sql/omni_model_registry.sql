-- OMNI Database — Model Registry Schema
-- Stores metadata about all active AI models in the OMNI cluster

CREATE TABLE IF NOT EXISTS omni_models (
    model_id UUID PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    architecture VARCHAR(100) NOT NULL,
    parameters_billion DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS omni_deployments (
    deployment_id UUID PRIMARY KEY,
    model_id UUID REFERENCES omni_models(model_id),
    node_group VARCHAR(255) NOT NULL,
    replicas INT NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast status lookups
CREATE INDEX idx_deployments_status ON omni_deployments(status);
