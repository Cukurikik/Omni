-- OMNI TEXT-GENERATION-INFERENCE: Inference Logs
-- PostgreSQL schema for tracking request latencies, token counts, and client metrics.
-- Source: huggingface/text-generation-inference

CREATE TABLE IF NOT EXISTS tgi_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    quantization_type VARCHAR(32), -- e.g., 'gptq', 'awq', 'none'
    deployed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tgi_requests (
    request_id UUID PRIMARY KEY,
    model_id INT NOT NULL REFERENCES tgi_models(id),
    client_ip VARCHAR(64),
    prompt_tokens INT NOT NULL,
    generated_tokens INT NOT NULL,
    total_latency_ms DOUBLE PRECISION NOT NULL,
    time_to_first_token_ms DOUBLE PRECISION NOT NULL,
    finish_reason VARCHAR(32), -- e.g., 'length', 'stop_sequence', 'eos'
    status VARCHAR(16) NOT NULL DEFAULT 'SUCCESS', -- 'SUCCESS', 'ERROR', 'CANCELLED'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for analytics queries (e.g. TPS, Latency p99)
CREATE INDEX idx_tgi_req_model_time ON tgi_requests(model_id, created_at DESC);
CREATE INDEX idx_tgi_req_status ON tgi_requests(status);

-- View for calculating basic real-time metrics
CREATE OR REPLACE VIEW v_tgi_metrics_hourly AS
SELECT 
    model_id,
    date_trunc('hour', created_at) as hour,
    count(*) as total_requests,
    sum(generated_tokens) as total_tokens,
    avg(total_latency_ms) as avg_latency_ms,
    percentile_cont(0.99) within group (order by time_to_first_token_ms) as p99_ttft_ms
FROM tgi_requests
WHERE status = 'SUCCESS'
GROUP BY model_id, date_trunc('hour', created_at);
