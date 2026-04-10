-- omni-popmotion Initial Migration
CREATE TABLE IF NOT EXISTS omni_popmotion_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_popmotion_status ON omni_popmotion_entities(status);
CREATE INDEX idx_omni_popmotion_created ON omni_popmotion_entities(created_at);