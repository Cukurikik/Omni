-- omni-parallax-core Initial Migration
CREATE TABLE IF NOT EXISTS omni_parallax_core_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_parallax_core_status ON omni_parallax_core_entities(status);
CREATE INDEX idx_omni_parallax_core_created ON omni_parallax_core_entities(created_at);