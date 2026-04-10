-- omni-supabase-storage Initial Migration
CREATE TABLE IF NOT EXISTS omni_supabase_storage_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_supabase_storage_status ON omni_supabase_storage_entities(status);
CREATE INDEX idx_omni_supabase_storage_created ON omni_supabase_storage_entities(created_at);