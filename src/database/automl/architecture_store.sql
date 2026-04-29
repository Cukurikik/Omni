-- Database: PostgreSQL
-- OMNI Framework Standards: Zero Mock, Strict Typing, Auditable Trails

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS automl_architecture_candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    architecture_hash VARCHAR(256) NOT NULL UNIQUE,
    hyperparameters JSONB NOT NULL,
    layers_definition JSONB NOT NULL,
    fitness_score DOUBLE PRECISION,
    accuracy DOUBLE PRECISION CHECK (accuracy >= 0.0 AND accuracy <= 1.0),
    latency_ms DOUBLE PRECISION CHECK (latency_ms > 0),
    memory_mb DOUBLE PRECISION CHECK (memory_mb > 0),
    is_evaluated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fitness ON automl_architecture_candidates(fitness_score DESC NULLS LAST);
CREATE INDEX idx_hash ON automl_architecture_candidates(architecture_hash);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_timestamp ON automl_architecture_candidates;
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON automl_architecture_candidates
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Policy for immutable history
CREATE TABLE IF NOT EXISTS automl_evaluation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES automl_architecture_candidates(id) ON DELETE CASCADE,
    previous_fitness DOUBLE PRECISION,
    new_fitness DOUBLE PRECISION,
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
