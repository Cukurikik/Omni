-- OMNI Framework - MoE Billing Ledger Schema (PostgreSQL)
-- Defines the database schema for recording precise token consumption
-- scaled by active expert parameter counts.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'standard',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS billing_ledger (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id),
    model_name VARCHAR(100) NOT NULL,
    
    -- Token tracking
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    
    -- MoE specific telemetry
    total_model_params_billions NUMERIC(8, 2) NOT NULL,
    active_params_billions NUMERIC(8, 2) NOT NULL,
    
    -- Financials
    cost_usd NUMERIC(12, 6) NOT NULL,
    
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast aggregation by tenant and time
CREATE INDEX idx_billing_ledger_tenant_time ON billing_ledger(tenant_id, timestamp);

-- Analytics View: Monthly Usage per Tenant
CREATE OR REPLACE VIEW v_monthly_invoice AS
SELECT 
    tenant_id,
    DATE_TRUNC('month', timestamp) AS invoice_month,
    SUM(prompt_tokens + completion_tokens) AS total_tokens,
    AVG(active_params_billions / total_model_params_billions) * 100 AS avg_active_param_percentage,
    SUM(cost_usd) AS total_cost_usd
FROM 
    billing_ledger
GROUP BY 
    tenant_id, invoice_month;
