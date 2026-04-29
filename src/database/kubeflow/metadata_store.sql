-- OMNI KUBEFLOW: ML Metadata (MLMD) Database Schema
-- Tracks artifacts, executions, and lineage of machine learning pipelines.
-- Source: kubeflow/pipelines

CREATE TABLE IF NOT EXISTS ContextType (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS Context (
    id SERIAL PRIMARY KEY,
    type_id INT NOT NULL REFERENCES ContextType(id),
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS ExecutionType (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS Execution (
    id SERIAL PRIMARY KEY,
    type_id INT NOT NULL REFERENCES ExecutionType(id),
    last_known_state VARCHAR(64) NOT NULL, -- e.g., RUNNING, COMPLETE, FAILED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ArtifactType (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS Artifact (
    id SERIAL PRIMARY KEY,
    type_id INT NOT NULL REFERENCES ArtifactType(id),
    uri TEXT NOT NULL,
    state VARCHAR(64) NOT NULL, -- e.g., PENDING, PUBLISHED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Lineage Tracking
CREATE TABLE IF NOT EXISTS Event (
    id SERIAL PRIMARY KEY,
    artifact_id INT NOT NULL REFERENCES Artifact(id),
    execution_id INT NOT NULL REFERENCES Execution(id),
    type VARCHAR(32) NOT NULL, -- e.g., INPUT, OUTPUT
    event_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Lineage Traversal
CREATE INDEX idx_event_execution ON Event(execution_id);
CREATE INDEX idx_event_artifact ON Event(artifact_id);
