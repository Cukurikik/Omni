-- omni-crypto-usdc Initial Migration
CREATE TABLE IF NOT EXISTS omni_crypto_usdc_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_crypto_usdc_status ON omni_crypto_usdc_entities(status);
CREATE INDEX idx_omni_crypto_usdc_created ON omni_crypto_usdc_entities(created_at);