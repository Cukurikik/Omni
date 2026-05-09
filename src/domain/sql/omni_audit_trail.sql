// OMNI Domain — SQL Model Audit Trail
-- Complete audit logging for model lifecycle events.

CREATE SCHEMA IF NOT EXISTS omni_audit;

CREATE TABLE omni_audit.model_events (
    event_id        BIGSERIAL PRIMARY KEY,
    event_type      VARCHAR(50) NOT NULL,
    model_id        UUID NOT NULL,
    model_name      VARCHAR(255),
    version         VARCHAR(50),
    actor_id        VARCHAR(100) NOT NULL,
    actor_role      VARCHAR(50),
    environment     VARCHAR(20),
    details         JSONB DEFAULT '{}',
    metadata        JSONB DEFAULT '{}',
    ip_address      INET,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_model ON omni_audit.model_events(model_id);
CREATE INDEX idx_audit_type ON omni_audit.model_events(event_type);
CREATE INDEX idx_audit_actor ON omni_audit.model_events(actor_id);
CREATE INDEX idx_audit_created ON omni_audit.model_events(created_at DESC);
CREATE INDEX idx_audit_env ON omni_audit.model_events(environment);

-- Model deployment history
CREATE TABLE omni_audit.deployment_history (
    deployment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id        UUID NOT NULL,
    version         VARCHAR(50) NOT NULL,
    environment     VARCHAR(20) NOT NULL CHECK (environment IN ('staging', 'production', 'edge')),
    replicas        INT NOT NULL DEFAULT 1,
    gpu_type        VARCHAR(50),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    deployed_by     VARCHAR(100) NOT NULL,
    deployed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rolled_back_at  TIMESTAMPTZ,
    rollback_reason TEXT,
    config          JSONB DEFAULT '{}',
    metrics_snapshot JSONB
);

CREATE INDEX idx_deploy_model ON omni_audit.deployment_history(model_id);
CREATE INDEX idx_deploy_env ON omni_audit.deployment_history(environment);
CREATE INDEX idx_deploy_status ON omni_audit.deployment_history(status);

-- Training run history  
CREATE TABLE omni_audit.training_runs (
    run_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id        UUID NOT NULL,
    version         VARCHAR(50),
    dataset_id      VARCHAR(255) NOT NULL,
    method          VARCHAR(50) NOT NULL DEFAULT 'sft',
    hyperparameters JSONB NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'queued',
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    final_loss      DOUBLE PRECISION,
    final_accuracy  DOUBLE PRECISION,
    gpu_hours       DOUBLE PRECISION,
    cost_usd        DOUBLE PRECISION,
    error_message   TEXT,
    artifacts       JSONB DEFAULT '[]'
);

CREATE INDEX idx_train_model ON omni_audit.training_runs(model_id);
CREATE INDEX idx_train_status ON omni_audit.training_runs(status);

-- Inference access logs for compliance
CREATE TABLE omni_audit.inference_access_log (
    log_id          BIGSERIAL PRIMARY KEY,
    request_id      UUID NOT NULL,
    model_id        UUID NOT NULL,
    user_id         VARCHAR(100),
    input_hash      VARCHAR(64),
    output_hash     VARCHAR(64),
    tokens_input    INT,
    tokens_output   INT,
    latency_ms      DOUBLE PRECISION,
    status_code     INT,
    flagged         BOOLEAN DEFAULT FALSE,
    flag_reason     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_access_model ON omni_audit.inference_access_log(model_id);
CREATE INDEX idx_access_user ON omni_audit.inference_access_log(user_id);
CREATE INDEX idx_access_flagged ON omni_audit.inference_access_log(flagged) WHERE flagged = TRUE;

-- Retention policy view
CREATE OR REPLACE VIEW omni_audit.retention_summary AS
SELECT 
    'model_events' AS table_name,
    COUNT(*) AS total_rows,
    MIN(created_at) AS oldest_record,
    MAX(created_at) AS newest_record
FROM omni_audit.model_events
UNION ALL
SELECT 'inference_access_log', COUNT(*), MIN(created_at), MAX(created_at)
FROM omni_audit.inference_access_log;
