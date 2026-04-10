-- omni-prettier-native Initial Migration
CREATE TABLE IF NOT EXISTS omni_prettier_native_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_prettier_native_status ON omni_prettier_native_entities(status);
CREATE INDEX idx_omni_prettier_native_created ON omni_prettier_native_entities(created_at);