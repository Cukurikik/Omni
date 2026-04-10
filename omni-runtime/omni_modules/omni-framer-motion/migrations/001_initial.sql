-- omni-framer-motion Initial Migration
CREATE TABLE IF NOT EXISTS omni_framer_motion_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_framer_motion_status ON omni_framer_motion_entities(status);
CREATE INDEX idx_omni_framer_motion_created ON omni_framer_motion_entities(created_at);