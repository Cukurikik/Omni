-- OMNI FEDML: Distributed Model Registry Schema
-- SQL DDL for tracking global models, federated rounds, and aggregated weights.
-- Source: FedML-AI/FedML

CREATE TABLE IF NOT EXISTS global_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(128) NOT NULL,
    architecture VARCHAR(128) NOT NULL,
    hyperparameters JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS aggregation_rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES global_models(id) ON DELETE CASCADE,
    round_number INT NOT NULL,
    participating_nodes INT NOT NULL,
    aggregation_method VARCHAR(64) NOT NULL DEFAULT 'FedAvg',
    global_loss DOUBLE PRECISION,
    global_accuracy DOUBLE PRECISION,
    weights_s3_uri TEXT NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_id, round_number)
);

CREATE TABLE IF NOT EXISTS node_contributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID NOT NULL REFERENCES aggregation_rounds(id) ON DELETE CASCADE,
    node_id VARCHAR(128) NOT NULL,
    samples_contributed INT NOT NULL,
    local_loss DOUBLE PRECISION,
    gradient_norm DOUBLE PRECISION,
    contributed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for tracking model convergence over time
CREATE INDEX idx_agg_rounds_model ON aggregation_rounds(model_id);
CREATE INDEX idx_agg_rounds_perf ON aggregation_rounds(global_accuracy DESC);
