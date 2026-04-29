-- OMNI Ploomber - Task Output Cache
-- Strict PostgreSQL schema for DAG task memoization

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS task_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dag_id VARCHAR(255) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    input_hash VARCHAR(64) NOT NULL,
    output_s3_uri VARCHAR(1024),
    execution_time_ms BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure uniqueness for caching
    UNIQUE(dag_id, task_name, code_hash, input_hash)
);

CREATE INDEX idx_task_cache ON task_executions(task_name, code_hash, input_hash);

-- Function to safely fetch cached output (Monadic emulation in SQL via strict returns)
CREATE OR REPLACE FUNCTION get_cached_output(
    p_task_name VARCHAR,
    p_code_hash VARCHAR,
    p_input_hash VARCHAR
) RETURNS VARCHAR AS $$
DECLARE
    v_output_uri VARCHAR;
BEGIN
    SELECT output_s3_uri INTO v_output_uri
    FROM task_executions
    WHERE task_name = p_task_name 
      AND code_hash = p_code_hash 
      AND input_hash = p_input_hash
    LIMIT 1;
    
    RETURN v_output_uri;
END;
$$ LANGUAGE plpgsql;
