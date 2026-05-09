-- OMNI Database — SQL Billing Ledger
-- Immutable ledger for tracking inference costs per tenant

CREATE TABLE IF NOT EXISTS omni_billing_ledger (
    transaction_id UUID PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    prompt_tokens INT NOT NULL,
    completion_tokens INT NOT NULL,
    cost_usd DECIMAL(12, 6) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_billing_tenant_time ON omni_billing_ledger(tenant_id, timestamp);

-- View for monthly aggregation
CREATE OR REPLACE VIEW omni_monthly_billing AS
SELECT 
    tenant_id,
    DATE_TRUNC('month', timestamp) as billing_month,
    SUM(prompt_tokens) as total_prompt_tokens,
    SUM(completion_tokens) as total_completion_tokens,
    SUM(cost_usd) as total_cost
FROM omni_billing_ledger
GROUP BY tenant_id, DATE_TRUNC('month', timestamp);
