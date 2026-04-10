-- omni-google-pay Initial Migration
CREATE TABLE IF NOT EXISTS omni_google_pay_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_google_pay_status ON omni_google_pay_entities(status);
CREATE INDEX idx_omni_google_pay_created ON omni_google_pay_entities(created_at);