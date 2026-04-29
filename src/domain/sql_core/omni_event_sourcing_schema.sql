-- Omni Event Sourcing Schema (SQL / Postgres)
-- Production-grade strict schema definition for Domain Event Bus

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS omni_domain_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_omni_events_aggregate ON omni_domain_events(aggregate_type, aggregate_id);
CREATE INDEX idx_omni_events_type ON omni_domain_events(event_type);

-- Constraint optimization: Payload must not be empty
ALTER TABLE omni_domain_events 
ADD CONSTRAINT check_payload_not_empty CHECK (payload != '{}'::jsonb);

COMMIT;
