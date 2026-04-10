-- omni-cloudflare-workers Initial Migration
CREATE TABLE IF NOT EXISTS omni_cloudflare_workers_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_cloudflare_workers_status ON omni_cloudflare_workers_entities(status);
CREATE INDEX idx_omni_cloudflare_workers_created ON omni_cloudflare_workers_entities(created_at);