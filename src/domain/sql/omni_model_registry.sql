-- OMNI Database Layer — SQL Schema for Model Registry & Experiment Tracking
-- Production schema for PostgreSQL with partitioning and indexes.

-- Model registry
CREATE TABLE IF NOT EXISTS omni_models (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    version         VARCHAR(50) NOT NULL,
    architecture    VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','training','validating','ready','deployed','deprecated','archived')),
    parameter_count BIGINT,
    model_size_mb   DOUBLE PRECISION,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by      VARCHAR(100),
    UNIQUE(name, version)
);

CREATE INDEX idx_models_status ON omni_models(status);
CREATE INDEX idx_models_name ON omni_models(name);
CREATE INDEX idx_models_created ON omni_models(created_at DESC);

-- Model metrics (training & evaluation)
CREATE TABLE IF NOT EXISTS omni_model_metrics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id    UUID NOT NULL REFERENCES omni_models(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    epoch       INT,
    step        BIGINT,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (recorded_at);

CREATE INDEX idx_metrics_model ON omni_model_metrics(model_id);
CREATE INDEX idx_metrics_name ON omni_model_metrics(metric_name);

-- Create monthly partitions
CREATE TABLE omni_model_metrics_2026_01 PARTITION OF omni_model_metrics
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE omni_model_metrics_2026_02 PARTITION OF omni_model_metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE omni_model_metrics_2026_03 PARTITION OF omni_model_metrics
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Experiment tracking
CREATE TABLE IF NOT EXISTS omni_experiments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id    UUID NOT NULL REFERENCES omni_models(id),
    name        VARCHAR(255) NOT NULL,
    config      JSONB NOT NULL DEFAULT '{}',
    status      VARCHAR(20) NOT NULL DEFAULT 'running'
                CHECK (status IN ('running','completed','failed','cancelled')),
    started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    results     JSONB
);

CREATE INDEX idx_experiments_model ON omni_experiments(model_id);
CREATE INDEX idx_experiments_status ON omni_experiments(status);

-- Deployment tracking
CREATE TABLE IF NOT EXISTS omni_deployments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id    UUID NOT NULL REFERENCES omni_models(id),
    environment VARCHAR(50) NOT NULL,
    region      VARCHAR(50) NOT NULL,
    replicas    INT NOT NULL DEFAULT 1,
    compute_type VARCHAR(50),
    endpoint_url VARCHAR(500),
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','deploying','active','draining','terminated')),
    deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    terminated_at TIMESTAMPTZ
);

CREATE INDEX idx_deployments_model ON omni_deployments(model_id);
CREATE INDEX idx_deployments_env ON omni_deployments(environment, status);

-- Inference logs (append-only, partitioned by time)
CREATE TABLE IF NOT EXISTS omni_inference_logs (
    id              UUID DEFAULT gen_random_uuid(),
    deployment_id   UUID NOT NULL,
    request_id      VARCHAR(64) NOT NULL,
    prompt_tokens   INT NOT NULL,
    completion_tokens INT NOT NULL,
    latency_ms      DOUBLE PRECISION NOT NULL,
    finish_reason   VARCHAR(20),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE INDEX idx_logs_deployment ON omni_inference_logs(deployment_id, created_at DESC);

-- Views for analytics
CREATE OR REPLACE VIEW omni_model_summary AS
SELECT
    m.id, m.name, m.version, m.architecture, m.status,
    m.parameter_count, m.model_size_mb,
    COUNT(DISTINCT d.id) AS active_deployments,
    COUNT(DISTINCT e.id) AS total_experiments,
    m.created_at, m.updated_at
FROM omni_models m
LEFT JOIN omni_deployments d ON d.model_id = m.id AND d.status = 'active'
LEFT JOIN omni_experiments e ON e.model_id = m.id
GROUP BY m.id;

-- Function: Update model timestamp on change
CREATE OR REPLACE FUNCTION update_model_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_model_updated
    BEFORE UPDATE ON omni_models
    FOR EACH ROW EXECUTE FUNCTION update_model_timestamp();
