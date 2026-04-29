-- OMNI SWANLAB: Experiment Schema
-- SQL schema for storing ML training run metadata, hyperparameters, and aggregated metrics.
-- Source: SwanHubX/SwanLab

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    run_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'RUNNING', -- RUNNING, COMPLETED, FAILED, CRASHED
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    hardware_env JSONB, -- Stores GPU type, CPU, RAM
    git_commit VARCHAR(64),
    UNIQUE(project_id, run_name)
);

CREATE TABLE IF NOT EXISTS hyperparameters (
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    param_key VARCHAR(128) NOT NULL,
    param_value JSONB NOT NULL,
    PRIMARY KEY (run_id, param_key)
);

CREATE TABLE IF NOT EXISTS run_metrics_summary (
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    metric_name VARCHAR(128) NOT NULL,
    best_value DOUBLE PRECISION,
    last_value DOUBLE PRECISION,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    PRIMARY KEY (run_id, metric_name)
);

-- Fast lookup indexes
CREATE INDEX idx_runs_project ON runs(project_id);
CREATE INDEX idx_metrics_run ON run_metrics_summary(run_id);
