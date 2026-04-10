-- omni-linode-obj Initial Migration
CREATE TABLE IF NOT EXISTS omni_linode_obj_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_linode_obj_status ON omni_linode_obj_entities(status);
CREATE INDEX idx_omni_linode_obj_created ON omni_linode_obj_entities(created_at);