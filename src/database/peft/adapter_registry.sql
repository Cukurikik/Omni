-- OMNI PEFT: Adapter Registry DDL
-- SQL tables mapping base HuggingFace models to available LoRA/QLoRA adapters.
-- Source: huggingface/peft

CREATE TABLE IF NOT EXISTS base_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) UNIQUE NOT NULL, -- e.g., 'meta-llama/Llama-2-7b-hf'
    architecture VARCHAR(64) NOT NULL,
    hidden_size INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lora_adapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_model_id UUID NOT NULL REFERENCES base_models(id) ON DELETE CASCADE,
    adapter_name VARCHAR(255) NOT NULL, -- e.g., 'finance-assistant-lora'
    rank_r INT NOT NULL DEFAULT 8,
    alpha DOUBLE PRECISION NOT NULL DEFAULT 16.0,
    target_modules JSONB NOT NULL, -- e.g., ["q_proj", "v_proj"]
    weights_s3_uri TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_model_id, adapter_name)
);

-- Indexing for fast adapter lookups when hot-swapping
CREATE INDEX idx_adapters_base_model ON lora_adapters(base_model_id);

-- View to list all available deployments
CREATE OR REPLACE VIEW v_available_deployments AS
SELECT 
    b.model_name as base_model,
    a.adapter_name,
    a.rank_r,
    a.target_modules
FROM lora_adapters a
JOIN base_models b ON a.base_model_id = b.id;
