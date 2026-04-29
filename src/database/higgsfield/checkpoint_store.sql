-- OMNI Higgsfield - Checkpoint Metadata Store
-- Strict PostgreSQL schema for managing distributed tensor checkpoints

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS training_jobs (
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) NOT NULL,
    total_parameters BIGINT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'RUNNING'
);

CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES training_jobs(job_id) ON DELETE CASCADE,
    epoch INT NOT NULL,
    step BIGINT NOT NULL,
    loss_value DOUBLE PRECISION,
    s3_uri VARCHAR(1024) NOT NULL,
    checksum VARCHAR(256) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkpoints_job ON checkpoints(job_id, epoch, step);

-- Monadic logic equivalent via strict constraints
ALTER TABLE checkpoints ADD CONSTRAINT chk_epoch_positive CHECK (epoch >= 0);
ALTER TABLE checkpoints ADD CONSTRAINT chk_step_positive CHECK (step >= 0);
