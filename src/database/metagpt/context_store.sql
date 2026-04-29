-- OMNI METAGPT: Context Store
-- SQL schema for persisting the entire conversation and artifact history of a multi-agent project.
-- Ensures agents can be paused and resumed without losing context.
-- Source: geekan/MetaGPT

CREATE TABLE IF NOT EXISTS metagpt_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    objective TEXT NOT NULL,
    status VARCHAR(64) DEFAULT 'planning', -- planning, coding, testing, completed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metagpt_messages (
    id SERIAL PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES metagpt_projects(id) ON DELETE CASCADE,
    sender_role VARCHAR(128) NOT NULL,
    receiver_role VARCHAR(128) NOT NULL,
    artifact_type VARCHAR(128) NOT NULL, -- PRD, API_SPEC, CODE, TEST
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast context retrieval for a specific agent
CREATE INDEX idx_metagpt_messages_project_receiver 
ON metagpt_messages(project_id, receiver_role);

-- View for assembling the full "Memory" of a project sequentially
CREATE OR REPLACE VIEW v_project_memory AS
SELECT 
    project_id,
    created_at,
    sender_role,
    artifact_type,
    content
FROM metagpt_messages
ORDER BY created_at ASC;
