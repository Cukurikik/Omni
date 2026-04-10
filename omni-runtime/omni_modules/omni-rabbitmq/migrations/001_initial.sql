-- omni-rabbitmq Initial Migration
CREATE TABLE IF NOT EXISTS omni_rabbitmq_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_rabbitmq_status ON omni_rabbitmq_entities(status);
CREATE INDEX idx_omni_rabbitmq_created ON omni_rabbitmq_entities(created_at);