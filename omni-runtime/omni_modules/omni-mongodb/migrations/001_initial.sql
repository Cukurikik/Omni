-- omni-mongodb Initial Migration
CREATE TABLE IF NOT EXISTS omni_mongodb_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_mongodb_status ON omni_mongodb_entities(status);
CREATE INDEX idx_omni_mongodb_created ON omni_mongodb_entities(created_at);