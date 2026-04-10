-- omni-graphql-federation Initial Migration
CREATE TABLE IF NOT EXISTS omni_graphql_federation_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_graphql_federation_status ON omni_graphql_federation_entities(status);
CREATE INDEX idx_omni_graphql_federation_created ON omni_graphql_federation_entities(created_at);