CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE postgresml.document_embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_text TEXT NOT NULL,
    embedding vector(768) NOT NULL
);

CREATE INDEX idx_pgml_embedding ON postgresml.document_embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
