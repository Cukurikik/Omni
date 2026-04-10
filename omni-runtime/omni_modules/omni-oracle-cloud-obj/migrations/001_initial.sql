-- omni-oracle-cloud-obj Initial Migration
CREATE TABLE IF NOT EXISTS omni_oracle_cloud_obj_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_oracle_cloud_obj_status ON omni_oracle_cloud_obj_entities(status);
CREATE INDEX idx_omni_oracle_cloud_obj_created ON omni_oracle_cloud_obj_entities(created_at);