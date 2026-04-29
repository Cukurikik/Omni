-- OMNI Engine: Paperless-ng PostgreSQL Schema
CREATE TABLE documents_document (
    id SERIAL PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    created TIMESTAMP WITH TIME ZONE NOT NULL,
    modified TIMESTAMP WITH TIME ZONE NOT NULL,
    checksum CHAR(32) UNIQUE NOT NULL,
    mime_type VARCHAR(256) NOT NULL,
    archive_serial_number INTEGER
);

CREATE TABLE documents_tag (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#a6cee3'
);

CREATE TABLE documents_document_tags (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents_document(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES documents_tag(id) ON DELETE CASCADE,
    UNIQUE(document_id, tag_id)
);

CREATE INDEX idx_document_checksum ON documents_document(checksum);
