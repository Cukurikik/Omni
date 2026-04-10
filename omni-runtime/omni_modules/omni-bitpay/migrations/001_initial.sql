-- omni-bitpay Initial Migration
CREATE TABLE IF NOT EXISTS omni_bitpay_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_bitpay_status ON omni_bitpay_entities(status);
CREATE INDEX idx_omni_bitpay_created ON omni_bitpay_entities(created_at);