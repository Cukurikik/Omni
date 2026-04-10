-- omni-influxdb Initial Migration
CREATE TABLE IF NOT EXISTS omni_influxdb_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_influxdb_status ON omni_influxdb_entities(status);
CREATE INDEX idx_omni_influxdb_created ON omni_influxdb_entities(created_at);