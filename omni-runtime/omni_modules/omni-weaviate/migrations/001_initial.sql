-- omni-weaviate Initial Migration
CREATE TABLE IF NOT EXISTS omni_weaviate_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_weaviate_status ON omni_weaviate_entities(status);
CREATE INDEX idx_omni_weaviate_created ON omni_weaviate_entities(created_at);