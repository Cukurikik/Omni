-- OMNI Database Layer: Kiln Evaluation Storage
-- Highly optimized PostgreSQL schema for storing RLHF / RAG evaluation metrics.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS kiln_datasets (
    dataset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kiln_evaluations (
    eval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id UUID NOT NULL REFERENCES kiln_datasets(dataset_id) ON DELETE CASCADE,
    prompt_hash VARCHAR(64) NOT NULL,
    candidate_response TEXT NOT NULL,
    score NUMERIC(5, 4) NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
    passed BOOLEAN NOT NULL,
    metrics_jsonb JSONB NOT NULL,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for fast retrieval and analytical aggregation
CREATE INDEX idx_eval_dataset ON kiln_evaluations(dataset_id);
CREATE INDEX idx_eval_passed ON kiln_evaluations(passed);
CREATE INDEX idx_eval_metrics_gin ON kiln_evaluations USING GIN (metrics_jsonb);

-- View for rapid dashboard aggregation
CREATE OR REPLACE VIEW kiln_daily_pass_rates AS
SELECT 
    DATE(evaluated_at) AS eval_date,
    dataset_id,
    COUNT(*) AS total_evals,
    SUM(CASE WHEN passed THEN 1 ELSE 0 END) AS passed_evals,
    ROUND(SUM(CASE WHEN passed THEN 1 ELSE 0 END)::NUMERIC / COUNT(*), 4) AS pass_rate
FROM kiln_evaluations
GROUP BY DATE(evaluated_at), dataset_id;
