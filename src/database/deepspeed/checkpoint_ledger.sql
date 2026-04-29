-- OMNI DEEPSPEED: Checkpoint Ledger
-- Tracks distributed checkpoints across multiple ZeRO ranks and storage volumes.
-- Source: microsoft/DeepSpeed

CREATE TABLE IF NOT EXISTS training_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    world_size INT NOT NULL,
    zero_stage INT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS global_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES training_runs(id) ON DELETE CASCADE,
    global_step INT NOT NULL,
    validation_loss DOUBLE PRECISION,
    is_latest BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rank_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    global_checkpoint_id UUID NOT NULL REFERENCES global_checkpoints(id) ON DELETE CASCADE,
    rank INT NOT NULL,
    s3_uri TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    checksum VARCHAR(128),
    UNIQUE(global_checkpoint_id, rank)
);

-- Indexing for quick retrieval during cluster recovery
CREATE INDEX idx_chkpt_run ON global_checkpoints(run_id, global_step DESC);
CREATE INDEX idx_rank_chkpt ON rank_checkpoints(global_checkpoint_id);
