-- OMNI Database Schema Migration V1
-- Target: PostgreSQL 14+

BEGIN;

CREATE TABLE IF NOT EXISTS omni_nodes (
    id UUID PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    layer VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'offline',
    last_heartbeat TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS omni_tasks (
    task_id UUID PRIMARY KEY,
    node_id UUID REFERENCES omni_nodes(id),
    payload JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_tasks_status ON omni_tasks(status);
CREATE INDEX idx_nodes_layer ON omni_nodes(layer);

COMMIT;
