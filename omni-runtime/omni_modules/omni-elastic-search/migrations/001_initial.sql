-- omni-elastic-search Initial Migration
CREATE TABLE IF NOT EXISTS omni_elastic_search_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_elastic_search_status ON omni_elastic_search_entities(status);
CREATE INDEX idx_omni_elastic_search_created ON omni_elastic_search_entities(created_at);