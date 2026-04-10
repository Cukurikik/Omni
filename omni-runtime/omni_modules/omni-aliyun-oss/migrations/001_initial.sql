-- omni-aliyun-oss Initial Migration
CREATE TABLE IF NOT EXISTS omni_aliyun_oss_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_aliyun_oss_status ON omni_aliyun_oss_entities(status);
CREATE INDEX idx_omni_aliyun_oss_created ON omni_aliyun_oss_entities(created_at);