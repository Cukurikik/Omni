-- OMNI Domain — SQL Inference Analytics Schema
-- Time-series analytics tables for inference performance monitoring.

CREATE TABLE IF NOT EXISTS inference_requests (
    id              BIGSERIAL PRIMARY KEY,
    request_id      UUID NOT NULL DEFAULT gen_random_uuid(),
    model_id        UUID NOT NULL,
    model_version   VARCHAR(50) NOT NULL,
    prompt_hash     VARCHAR(64) NOT NULL,
    prompt_tokens   INTEGER NOT NULL,
    output_tokens   INTEGER NOT NULL,
    latency_ms      FLOAT NOT NULL,
    gpu_ms          FLOAT,
    queue_ms        FLOAT,
    status          VARCHAR(20) NOT NULL DEFAULT 'completed'
                    CHECK (status IN ('completed','error','timeout','cancelled')),
    error_code      VARCHAR(50),
    client_ip       INET,
    user_agent      VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_performance_hourly (
    id              BIGSERIAL PRIMARY KEY,
    model_id        UUID NOT NULL,
    hour            TIMESTAMPTZ NOT NULL,
    total_requests  BIGINT NOT NULL DEFAULT 0,
    error_count     BIGINT NOT NULL DEFAULT 0,
    avg_latency_ms  FLOAT NOT NULL DEFAULT 0,
    p50_latency_ms  FLOAT,
    p95_latency_ms  FLOAT,
    p99_latency_ms  FLOAT,
    total_tokens    BIGINT NOT NULL DEFAULT 0,
    avg_throughput  FLOAT,
    UNIQUE(model_id, hour)
);

CREATE TABLE IF NOT EXISTS gpu_utilization (
    id              BIGSERIAL PRIMARY KEY,
    node_id         VARCHAR(100) NOT NULL,
    gpu_index       INTEGER NOT NULL,
    utilization_pct FLOAT NOT NULL,
    memory_used_mb  BIGINT NOT NULL,
    memory_total_mb BIGINT NOT NULL,
    temperature_c   FLOAT,
    power_watts     FLOAT,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partitioned by time for performance
CREATE INDEX idx_requests_time ON inference_requests(created_at DESC);
CREATE INDEX idx_requests_model ON inference_requests(model_id, created_at DESC);
CREATE INDEX idx_perf_model ON model_performance_hourly(model_id, hour DESC);
CREATE INDEX idx_gpu_node ON gpu_utilization(node_id, recorded_at DESC);

-- Materialized view: Real-time dashboard data
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_model_dashboard AS
SELECT model_id, model_version,
       COUNT(*) as total_requests,
       AVG(latency_ms) as avg_latency,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
       SUM(output_tokens) as total_tokens,
       COUNT(*) FILTER (WHERE status = 'error') as error_count,
       MAX(created_at) as last_request
FROM inference_requests
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY model_id, model_version;
