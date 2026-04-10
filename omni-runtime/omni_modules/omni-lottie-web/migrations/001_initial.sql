-- omni-lottie-web Initial Migration
CREATE TABLE IF NOT EXISTS omni_lottie_web_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_lottie_web_status ON omni_lottie_web_entities(status);
CREATE INDEX idx_omni_lottie_web_created ON omni_lottie_web_entities(created_at);