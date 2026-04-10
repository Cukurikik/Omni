-- omni-auth-jwt Initial Migration
CREATE TABLE IF NOT EXISTS omni_auth_jwt_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_auth_jwt_status ON omni_auth_jwt_entities(status);
CREATE INDEX idx_omni_auth_jwt_created ON omni_auth_jwt_entities(created_at);