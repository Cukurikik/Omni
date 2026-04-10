-- omni-backblaze-b2 Initial Migration
CREATE TABLE IF NOT EXISTS omni_backblaze_b2_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_backblaze_b2_status ON omni_backblaze_b2_entities(status);
CREATE INDEX idx_omni_backblaze_b2_created ON omni_backblaze_b2_entities(created_at);