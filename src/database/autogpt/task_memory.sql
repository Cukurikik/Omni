-- OMNI AUTOGPT: Task & Execution Memory
-- Relational tables for storing agent goals, executed actions, and outcomes.
-- Source: Significant-Gravitas/AutoGPT

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    objective TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'RUNNING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS goal_trees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES goal_trees(id),
    description TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS executed_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID NOT NULL REFERENCES goal_trees(id),
    tool_name VARCHAR(128) NOT NULL,
    parameters JSONB NOT NULL,
    result TEXT,
    is_success BOOLEAN NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing to reconstruct an agent's execution history rapidly
CREATE INDEX idx_goal_trees_agent ON goal_trees(agent_id);
CREATE INDEX idx_executed_actions_goal ON executed_actions(goal_id);
CREATE INDEX idx_executed_actions_success ON executed_actions(is_success);
