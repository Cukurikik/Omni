-- omni-paypal Initial Migration
CREATE TABLE IF NOT EXISTS omni_paypal_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_paypal_status ON omni_paypal_entities(status);
CREATE INDEX idx_omni_paypal_created ON omni_paypal_entities(created_at);