-- omni-timescaledb Initial Migration
CREATE TABLE IF NOT EXISTS omni_timescaledb_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_timescaledb_status ON omni_timescaledb_entities(status);
CREATE INDEX idx_omni_timescaledb_created ON omni_timescaledb_entities(created_at);