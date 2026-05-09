-- OMNI Framework - MoE Audit Log Schema (PostgreSQL)
-- Secure, append-only schema for tracking sensitive requests,
-- policy evaluations, and system configurations for compliance (SOC2/HIPAA).

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS security_audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    tenant_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    
    event_type VARCHAR(100) NOT NULL, -- e.g., 'inference_request', 'policy_denial', 'expert_reconfiguration'
    resource VARCHAR(255) NOT NULL,   -- e.g., 'moe_endpoint_v1', 'cerbos_policy_engine'
    action VARCHAR(100) NOT NULL,
    
    status VARCHAR(50) NOT NULL,      -- 'SUCCESS', 'DENIED', 'ERROR'
    
    -- IP Address and User Agent for tracing
    client_ip INET NOT NULL,
    user_agent TEXT,
    
    -- JSON payload detailing the event (e.g., prompt hash, requested experts)
    -- NEVER log plain text prompts in the audit log for privacy reasons.
    event_metadata JSONB
);

-- Indexes for fast compliance querying
CREATE INDEX idx_audit_tenant_time ON security_audit_log(tenant_id, timestamp);
CREATE INDEX idx_audit_event_type ON security_audit_log(event_type);

-- Example query for security review
-- SELECT * FROM security_audit_log WHERE status = 'DENIED' AND timestamp >= NOW() - INTERVAL '24 HOURS';
