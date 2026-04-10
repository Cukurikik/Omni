-- omni-alipay Initial Migration
CREATE TABLE IF NOT EXISTS omni_alipay_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_alipay_status ON omni_alipay_entities(status);
CREATE INDEX idx_omni_alipay_created ON omni_alipay_entities(created_at);