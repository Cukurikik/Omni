CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(255) NOT NULL,
    accuracy DECIMAL(5,4) NOT NULL,
    p99_latency DECIMAL(8,2) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_metrics_model_id ON model_metrics(model_id);
