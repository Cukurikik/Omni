-- OMNI PROMPTPAPERS: Tuning Experiments DDL
-- Tracks iterations and parameters of prompt-tuning for foundation models.
-- Source: thunlp/PromptPapers

CREATE TABLE IF NOT EXISTS prompt_tuning_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(128) NOT NULL,
    template_id UUID NOT NULL,
    learning_rate DOUBLE PRECISION NOT NULL,
    batch_size INT NOT NULL,
    epochs INT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'INITIALIZED',
    final_loss DOUBLE PRECISION,
    validation_accuracy DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prompt_soft_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES prompt_tuning_experiments(id) ON DELETE CASCADE,
    token_index INT NOT NULL,
    embedding_vector FLOAT8[] NOT NULL, -- Storing the actual continuous prompt tensor
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for fast retrieval of best experiments
CREATE INDEX idx_pt_exp_model ON prompt_tuning_experiments(model_name);
CREATE INDEX idx_pt_exp_accuracy ON prompt_tuning_experiments(validation_accuracy DESC);
