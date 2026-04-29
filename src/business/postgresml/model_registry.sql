CREATE SCHEMA IF NOT EXISTS postgresml;

CREATE TABLE postgresml.models (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    hyperparams JSONB DEFAULT '{}'::jsonb,
    weights BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_postgresml_model_name ON postgresml.models(name);
