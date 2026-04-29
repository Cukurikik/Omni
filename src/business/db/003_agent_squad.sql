CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'queued',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_status ON agent_tasks(status);
