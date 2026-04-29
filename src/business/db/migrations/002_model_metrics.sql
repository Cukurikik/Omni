CREATE TABLE model_metrics (
    id UUID PRIMARY KEY,
    model_id UUID NOT NULL,
    accuracy FLOAT NOT NULL,
    latency_ms FLOAT NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_metrics_model ON model_metrics(model_id);
