-- omni-postgresql Initial Migration
CREATE TABLE IF NOT EXISTS omni_postgresql_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_postgresql_status ON omni_postgresql_entities(status);
CREATE INDEX idx_omni_postgresql_created ON omni_postgresql_entities(created_at);