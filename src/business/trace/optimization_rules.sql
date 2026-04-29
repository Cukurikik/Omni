-- OmniResult standard wrapper for Trace optimization rules
CREATE OR REPLACE FUNCTION trace_evaluate_agent_workflow(workflow_id UUID)
RETURNS JSONB AS $$
DECLARE
    total_latency FLOAT;
    error_msg TEXT;
BEGIN
    IF workflow_id IS NULL THEN
        RETURN jsonb_build_object('value', NULL, 'error', 'Invalid workflow ID', 'is_ok', false);
    END IF;

    SELECT SUM(step_latency) INTO total_latency
    FROM workflow_traces
    WHERE workflow = workflow_id;

    IF total_latency IS NULL THEN
        total_latency := 0.0;
    END IF;

    RETURN jsonb_build_object(
        'value', jsonb_build_object('total_latency', total_latency, 'needs_optimization', total_latency > 5000.0),
        'error', NULL,
        'is_ok', true
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN jsonb_build_object('value', NULL, 'error', SQLERRM, 'is_ok', false);
END;
$$ LANGUAGE plpgsql;
