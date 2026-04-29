-- OMNI Business Layer: maxtext_quota.sql
-- Tracks MaxText TPU compute quota usage per project.
-- Bounds: Max 100,000 compute hours per project record.

CREATE TABLE maxtext_tpu_quota (
    project_id UUID PRIMARY KEY,
    allocated_hours DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    used_hours DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_quota_bounds CHECK (allocated_hours <= 100000.00),
    CONSTRAINT check_usage_bounds CHECK (used_hours <= allocated_hours)
);

-- Trigger to simulate monadic error mapping on bounded failure
CREATE OR REPLACE FUNCTION check_quota_limits()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.used_hours > NEW.allocated_hours THEN
        RAISE EXCEPTION 'OMNI_ERR_1: TPU Quota Exceeded bounds for project %', NEW.project_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_maxtext_quota
BEFORE UPDATE ON maxtext_tpu_quota
FOR EACH ROW EXECUTE FUNCTION check_quota_limits();
