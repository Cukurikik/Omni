-- omni-webpack-killer Initial Migration
CREATE TABLE IF NOT EXISTS omni_webpack_killer_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_webpack_killer_status ON omni_webpack_killer_entities(status);
CREATE INDEX idx_omni_webpack_killer_created ON omni_webpack_killer_entities(created_at);