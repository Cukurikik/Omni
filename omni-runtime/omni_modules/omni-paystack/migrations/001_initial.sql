-- omni-paystack Initial Migration
CREATE TABLE IF NOT EXISTS omni_paystack_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_paystack_status ON omni_paystack_entities(status);
CREATE INDEX idx_omni_paystack_created ON omni_paystack_entities(created_at);