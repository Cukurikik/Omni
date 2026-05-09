-- @omni-layer Business | @omni-source huggingface/text-generation-inference
-- @omni-description TGI inference audit schema: request tracking, latency metrics,
-- SLA compliance, and throughput monitoring.
-- @omni-lang SQL | @omni-batch 16 | @omni-semester 16

CREATE TABLE IF NOT EXISTS tgi_inference_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id VARCHAR(128) NOT NULL,
    model_version VARCHAR(64),
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    max_new_tokens INTEGER,
    temperature FLOAT,
    top_p FLOAT,
    total_latency_ms DOUBLE PRECISION NOT NULL,
    time_to_first_token_ms DOUBLE PRECISION,
    tokens_per_second DOUBLE PRECISION,
    batch_size INTEGER DEFAULT 1,
    speculative_accepted INTEGER DEFAULT 0,
    status VARCHAR(32) DEFAULT 'completed',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tgi_model_health (
    id BIGSERIAL PRIMARY KEY,
    model_id VARCHAR(128) NOT NULL,
    active_requests INTEGER DEFAULT 0,
    queue_depth INTEGER DEFAULT 0,
    gpu_memory_used_mb DOUBLE PRECISION,
    gpu_utilization_pct DOUBLE PRECISION,
    cache_hit_rate DOUBLE PRECISION,
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tgi_sla_violations (
    id BIGSERIAL PRIMARY KEY,
    request_id UUID REFERENCES tgi_inference_requests(request_id),
    violation_type VARCHAR(64) NOT NULL,
    threshold_ms DOUBLE PRECISION,
    actual_ms DOUBLE PRECISION,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tgi_requests_model ON tgi_inference_requests(model_id);
CREATE INDEX idx_tgi_requests_time ON tgi_inference_requests(created_at);
CREATE INDEX idx_tgi_health_model ON tgi_model_health(model_id);
CREATE INDEX idx_tgi_sla_type ON tgi_sla_violations(violation_type);
