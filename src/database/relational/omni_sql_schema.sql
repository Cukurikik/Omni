-- Omni Relational Schema (SQL)
-- Database Layer
-- Robust PostgreSQL schema for storing model metadata, training epochs, 
-- and distributed node topology.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS omni_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    billing_tier VARCHAR(50) DEFAULT 'community',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS omni_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES omni_organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    architecture VARCHAR(100) NOT NULL,
    total_parameters BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_model_name_per_org UNIQUE(org_id, name)
);

CREATE TABLE IF NOT EXISTS omni_training_epochs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES omni_models(id) ON DELETE CASCADE,
    epoch_number INTEGER NOT NULL,
    training_loss DOUBLE PRECISION,
    validation_loss DOUBLE PRECISION,
    checkpoint_s3_path TEXT NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_epoch_per_model UNIQUE(model_id, epoch_number)
);

CREATE TABLE IF NOT EXISTS omni_cluster_nodes (
    node_id VARCHAR(100) PRIMARY KEY,
    ip_address INET NOT NULL,
    region VARCHAR(50) NOT NULL,
    total_vram_mb INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'ONLINE',
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookup of active models and their latest epochs
CREATE INDEX idx_models_active ON omni_models(org_id, is_active);
CREATE INDEX idx_epochs_model_completed ON omni_training_epochs(model_id, completed_at DESC);
