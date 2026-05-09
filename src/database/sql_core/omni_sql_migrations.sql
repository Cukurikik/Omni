-- OMNI Database Layer: SQL Migrations
CREATE TABLE omni_nodes (
    id UUID PRIMARY KEY,
    metadata JSONB NOT NULL
);
