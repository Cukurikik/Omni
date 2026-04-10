-- omni-date-fns Initial Migration
CREATE TABLE IF NOT EXISTS omni_date_fns_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_date_fns_status ON omni_date_fns_entities(status);
CREATE INDEX idx_omni_date_fns_created ON omni_date_fns_entities(created_at);