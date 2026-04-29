-- OMNI STANFORD ALPACA: Instruction Dataset DDL
-- SQL tables designed to store generated self-instruct datasets for fine-tuning LLMs.
-- Source: tatsu-lab/stanford_alpaca

CREATE TABLE IF NOT EXISTS instruction_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_model VARCHAR(128) NOT NULL, -- e.g., 'text-davinci-003'
    prompt_template TEXT NOT NULL,
    total_generated INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instruction_pairs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES instruction_runs(id) ON DELETE CASCADE,
    instruction TEXT NOT NULL,
    input TEXT, -- Optional context
    output TEXT NOT NULL, -- The target generated response
    quality_score DOUBLE PRECISION, -- Evaluated via a reward model or human rating
    is_filtered BOOLEAN DEFAULT FALSE, -- Filtered if too similar to existing or toxic
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for semantic filtering and rapid dataset exports
CREATE INDEX idx_inst_pairs_run ON instruction_pairs(run_id);
CREATE INDEX idx_inst_pairs_filtered ON instruction_pairs(is_filtered) WHERE is_filtered = FALSE;

-- View for exporting final training dataset
CREATE OR REPLACE VIEW v_clean_instruction_dataset AS
SELECT instruction, input, output
FROM instruction_pairs
WHERE is_filtered = FALSE 
  AND quality_score > 0.7;
