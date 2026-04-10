-- omni-coinbase-commerce Initial Migration
CREATE TABLE IF NOT EXISTS omni_coinbase_commerce_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_coinbase_commerce_status ON omni_coinbase_commerce_entities(status);
CREATE INDEX idx_omni_coinbase_commerce_created ON omni_coinbase_commerce_entities(created_at);