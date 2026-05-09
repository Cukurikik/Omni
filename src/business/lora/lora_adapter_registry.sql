-- @omni-layer Business | @omni-source huggingface/peft | @omni-lang SQL
-- @omni-description LoRA adapter registry: stores adapter configurations,
-- training history, and deployment status.

CREATE TABLE IF NOT EXISTS lora_adapters (
    adapter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_model VARCHAR(256) NOT NULL,
    adapter_name VARCHAR(128) NOT NULL UNIQUE,
    rank INTEGER NOT NULL DEFAULT 8,
    alpha FLOAT NOT NULL DEFAULT 16,
    target_modules TEXT[] NOT NULL DEFAULT '{"q_proj","v_proj"}',
    trainable_params BIGINT,
    total_params BIGINT,
    param_ratio DOUBLE PRECISION GENERATED ALWAYS AS (
        CASE WHEN total_params > 0 THEN trainable_params::double precision / total_params ELSE 0 END
    ) STORED,
    status VARCHAR(32) DEFAULT 'training',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lora_training_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adapter_id UUID REFERENCES lora_adapters(adapter_id),
    dataset_name VARCHAR(256),
    n_epochs INTEGER,
    learning_rate DOUBLE PRECISION,
    batch_size INTEGER,
    final_loss DOUBLE PRECISION,
    best_val_loss DOUBLE PRECISION,
    training_time_sec DOUBLE PRECISION,
    status VARCHAR(32) DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS lora_deployments (
    deployment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adapter_id UUID REFERENCES lora_adapters(adapter_id),
    endpoint_url VARCHAR(512),
    traffic_weight DOUBLE PRECISION DEFAULT 1.0,
    total_requests BIGINT DEFAULT 0,
    avg_latency_ms DOUBLE PRECISION,
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_lora_adapters_model ON lora_adapters(base_model);
CREATE INDEX idx_lora_runs_adapter ON lora_training_runs(adapter_id);
CREATE INDEX idx_lora_deploy_adapter ON lora_deployments(adapter_id);
