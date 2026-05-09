-- @omni-layer Database | @omni-lang SQL | @omni-batch 18 | @omni-semester 16
-- @omni-description SQL schema for transformer model registry, inference logs,
-- knowledge edit audit, and performance metrics storage.

-- === Model Registry ===
CREATE TABLE IF NOT EXISTS omni_models (
    model_id VARCHAR(128) PRIMARY KEY,
    model_type VARCHAR(64) NOT NULL,
    version VARCHAR(32) NOT NULL,
    d_model INT NOT NULL DEFAULT 768,
    n_heads INT NOT NULL DEFAULT 12,
    n_layers INT NOT NULL DEFAULT 12,
    params_million DECIMAL(12,2),
    checkpoint_uri TEXT,
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_models_type ON omni_models(model_type);
CREATE INDEX idx_models_status ON omni_models(status);

-- === Inference Logs ===
CREATE TABLE IF NOT EXISTS omni_inference_logs (
    log_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    request_id VARCHAR(64) NOT NULL,
    model_id VARCHAR(128) NOT NULL REFERENCES omni_models(model_id),
    user_id VARCHAR(128),
    input_tokens INT,
    output_tokens INT,
    latency_ms DECIMAL(10,2),
    throughput_tps DECIMAL(10,2),
    gpu_utilization DECIMAL(5,2),
    memory_mb DECIMAL(10,2),
    status VARCHAR(32) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_model ON omni_inference_logs(model_id, created_at);
CREATE INDEX idx_logs_user ON omni_inference_logs(user_id, created_at);
CREATE INDEX idx_logs_status ON omni_inference_logs(status);

-- === Knowledge Edit Audit ===
CREATE TABLE IF NOT EXISTS omni_knowledge_edits (
    edit_id VARCHAR(64) PRIMARY KEY,
    model_id VARCHAR(128) NOT NULL REFERENCES omni_models(model_id),
    editor_id VARCHAR(128) NOT NULL,
    subject TEXT NOT NULL,
    relation TEXT NOT NULL,
    old_object TEXT NOT NULL,
    new_object TEXT NOT NULL,
    target_layer INT,
    verified BOOLEAN DEFAULT FALSE,
    verification_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_edits_model ON omni_knowledge_edits(model_id);
CREATE INDEX idx_edits_subject ON omni_knowledge_edits(subject);

-- === Performance Metrics ===
CREATE TABLE IF NOT EXISTS omni_model_metrics (
    metric_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    model_id VARCHAR(128) NOT NULL REFERENCES omni_models(model_id),
    metric_name VARCHAR(64) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    dataset VARCHAR(128),
    split VARCHAR(32),
    epoch INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_model ON omni_model_metrics(model_id, metric_name);

-- === Seed Data ===
INSERT INTO omni_models (model_id, model_type, version, d_model, n_heads, n_layers, params_million) VALUES
('tempo-forecaster', 'timeseries', '1.0.0', 768, 12, 6, 125.0),
('hiformer-seg', 'segmentation', '1.0.0', 256, 8, 4, 85.0),
('video-classifier', 'video', '1.0.0', 768, 12, 12, 300.0),
('bert-ner', 'ner', '1.0.0', 768, 12, 12, 110.0),
('long-text-cls', 'classification', '1.0.0', 768, 12, 12, 110.0),
('knowledge-editor', 'editing', '1.0.0', 768, 12, 12, 110.0),
('awex-sync', 'weight_sync', '1.0.0', 0, 0, 0, 0.0);

-- === Views ===
CREATE OR REPLACE VIEW omni_model_performance AS
SELECT m.model_id, m.model_type, m.version,
       AVG(l.latency_ms) AS avg_latency_ms,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY l.latency_ms) AS p95_latency_ms,
       SUM(l.input_tokens + l.output_tokens) AS total_tokens,
       COUNT(*) AS total_requests,
       SUM(CASE WHEN l.status = 'error' THEN 1 ELSE 0 END) AS error_count
FROM omni_models m
LEFT JOIN omni_inference_logs l ON m.model_id = l.model_id
GROUP BY m.model_id, m.model_type, m.version;

CREATE OR REPLACE VIEW omni_edit_audit AS
SELECT ke.edit_id, ke.model_id, ke.editor_id, ke.subject, ke.relation,
       ke.old_object, ke.new_object, ke.verified, ke.verification_score,
       ke.created_at
FROM omni_knowledge_edits ke
ORDER BY ke.created_at DESC;
