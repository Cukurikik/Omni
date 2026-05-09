-- OMNI Framework - Transformer Metrics SQL Schema
-- Stores billing and performance telemetry for LLM requests

CREATE TABLE IF NOT EXISTS tenant_usage_metrics (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    request_id VARCHAR(255) NOT NULL UNIQUE,
    model_name VARCHAR(100) NOT NULL,
    input_tokens INT NOT NULL DEFAULT 0,
    output_tokens INT NOT NULL DEFAULT 0,
    total_latency_ms INT NOT NULL,
    time_to_first_token_ms INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenant_metrics ON tenant_usage_metrics(tenant_id, created_at);
CREATE INDEX idx_model_usage ON tenant_usage_metrics(model_name, created_at);

-- Daily aggregation view for billing dashboards
CREATE OR REPLACE VIEW daily_tenant_billing AS
SELECT 
    tenant_id,
    DATE(created_at) as usage_date,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    COUNT(id) as total_requests,
    AVG(total_latency_ms) as avg_latency
FROM 
    tenant_usage_metrics
GROUP BY 
    tenant_id, DATE(created_at);
