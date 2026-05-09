-- @omni-layer Business | @omni-source calebevans/cordon | @omni-lang SQL
-- @omni-description Log analytics store: relational schema for log templates,
-- anomaly events, alert rules, and aggregated log statistics.

CREATE TABLE IF NOT EXISTS omni_log_sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    source_type     VARCHAR(50) NOT NULL CHECK(source_type IN ('application','infrastructure','security','network')),
    host            VARCHAR(255),
    environment     VARCHAR(50) DEFAULT 'production',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS omni_log_templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID NOT NULL REFERENCES omni_log_sources(id),
    template_text   TEXT NOT NULL,
    occurrence_count BIGINT NOT NULL DEFAULT 1,
    severity        VARCHAR(20) DEFAULT 'info' CHECK(severity IN ('debug','info','warning','error','critical')),
    first_seen      TIMESTAMP DEFAULT NOW(),
    last_seen       TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_id, template_text)
);

CREATE INDEX IF NOT EXISTS idx_template_source ON omni_log_templates(source_id);
CREATE INDEX IF NOT EXISTS idx_template_severity ON omni_log_templates(severity);

CREATE TABLE IF NOT EXISTS omni_anomaly_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID NOT NULL REFERENCES omni_log_sources(id),
    template_id     UUID REFERENCES omni_log_templates(id),
    raw_line        TEXT NOT NULL,
    anomaly_score   FLOAT8 NOT NULL,
    detection_method VARCHAR(50) DEFAULT 'embedding_distance',
    acknowledged    BOOLEAN DEFAULT FALSE,
    resolved        BOOLEAN DEFAULT FALSE,
    detected_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomaly_source ON omni_anomaly_events(source_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_score ON omni_anomaly_events(anomaly_score DESC);

CREATE TABLE IF NOT EXISTS omni_alert_rules (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID REFERENCES omni_log_sources(id),
    rule_name       VARCHAR(255) NOT NULL,
    condition_type  VARCHAR(50) NOT NULL CHECK(condition_type IN ('anomaly_rate','error_rate','frequency','custom')),
    threshold       FLOAT8 NOT NULL,
    window_minutes  INT NOT NULL DEFAULT 5,
    webhook_url     TEXT,
    is_enabled      BOOLEAN DEFAULT TRUE,
    last_triggered  TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- View: hourly anomaly summary
CREATE OR REPLACE VIEW omni_hourly_anomaly_summary AS
SELECT
    source_id,
    date_trunc('hour', detected_at) AS hour,
    COUNT(*) AS total_anomalies,
    AVG(anomaly_score) AS avg_score,
    MAX(anomaly_score) AS max_score,
    COUNT(*) FILTER (WHERE acknowledged) AS acknowledged,
    COUNT(*) FILTER (WHERE resolved) AS resolved
FROM omni_anomaly_events
GROUP BY source_id, date_trunc('hour', detected_at);
