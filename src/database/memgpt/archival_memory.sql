-- OMNI MEMGPT: Archival Memory Database
-- Relational structures to hold the "infinite" paged-out memory of the agent.
-- Source: memgpt/MemGPT

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    system_prompt TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    block_type VARCHAR(32) NOT NULL, -- e.g., 'persona', 'human'
    content TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS archival_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL, -- 'user', 'assistant', 'system', 'tool'
    content TEXT NOT NULL,
    embedding FLOAT8[], -- Vector representation for semantic retrieval
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for fast semantic search (pgvector assumed in production)
-- CREATE INDEX ON archival_messages USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_archival_agent_time ON archival_messages(agent_id, timestamp DESC);
