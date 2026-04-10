-- omni-image-optimizer Initial Migration
CREATE TABLE IF NOT EXISTS omni_image_optimizer_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_image_optimizer_status ON omni_image_optimizer_entities(status);
CREATE INDEX idx_omni_image_optimizer_created ON omni_image_optimizer_entities(created_at);