-- omni-authorize-net Initial Migration
CREATE TABLE IF NOT EXISTS omni_authorize_net_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_authorize_net_status ON omni_authorize_net_entities(status);
CREATE INDEX idx_omni_authorize_net_created ON omni_authorize_net_entities(created_at);