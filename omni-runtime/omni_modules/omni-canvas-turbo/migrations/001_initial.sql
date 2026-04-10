-- omni-canvas-turbo Initial Migration
CREATE TABLE IF NOT EXISTS omni_canvas_turbo_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_canvas_turbo_status ON omni_canvas_turbo_entities(status);
CREATE INDEX idx_omni_canvas_turbo_created ON omni_canvas_turbo_entities(created_at);