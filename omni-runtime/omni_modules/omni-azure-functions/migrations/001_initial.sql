-- omni-azure-functions Initial Migration
CREATE TABLE IF NOT EXISTS omni_azure_functions_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_azure_functions_status ON omni_azure_functions_entities(status);
CREATE INDEX idx_omni_azure_functions_created ON omni_azure_functions_entities(created_at);