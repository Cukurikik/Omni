-- OMNI SUPABASE: Row Level Security (RLS)
-- SQL schema enforcing strict Row Level Security policies for multi-tenant applications.
-- Source: supabase/supabase

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS tenant_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Force RLS on the table
ALTER TABLE tenant_data ENABLE ROW LEVEL SECURITY;

-- Policy: Tenants can only READ their own data
CREATE POLICY tenant_read_policy ON tenant_data
    FOR SELECT
    USING (
        tenant_id = current_setting('request.jwt.claim.sub', true)::UUID
    );

-- Policy: Tenants can only INSERT their own data
CREATE POLICY tenant_insert_policy ON tenant_data
    FOR INSERT
    WITH CHECK (
        tenant_id = current_setting('request.jwt.claim.sub', true)::UUID
    );

-- Policy: Tenants can only UPDATE their own data
CREATE POLICY tenant_update_policy ON tenant_data
    FOR UPDATE
    USING (
        tenant_id = current_setting('request.jwt.claim.sub', true)::UUID
    )
    WITH CHECK (
        tenant_id = current_setting('request.jwt.claim.sub', true)::UUID
    );

-- Policy: Tenants can only DELETE their own data
CREATE POLICY tenant_delete_policy ON tenant_data
    FOR DELETE
    USING (
        tenant_id = current_setting('request.jwt.claim.sub', true)::UUID
    );

-- Create highly optimized index for RLS lookups
CREATE INDEX idx_tenant_data_tenant_id ON tenant_data(tenant_id);
