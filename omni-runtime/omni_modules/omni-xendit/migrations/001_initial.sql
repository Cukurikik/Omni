-- omni-xendit Initial Migration
CREATE TABLE IF NOT EXISTS omni_xendit_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_xendit_status ON omni_xendit_entities(status);
CREATE INDEX idx_omni_xendit_created ON omni_xendit_entities(created_at);