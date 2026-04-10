-- omni-wasabi-s3 Initial Migration
CREATE TABLE IF NOT EXISTS omni_wasabi_s3_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_wasabi_s3_status ON omni_wasabi_s3_entities(status);
CREATE INDEX idx_omni_wasabi_s3_created ON omni_wasabi_s3_entities(created_at);