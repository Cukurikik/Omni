-- OmniResult standard wrapper for SQL procedures
CREATE OR REPLACE FUNCTION agent_gym_calculate_reward(agent_id UUID, episode_id UUID)
RETURNS JSONB AS $$
DECLARE
    total_reward FLOAT;
    error_msg TEXT;
BEGIN
    IF agent_id IS NULL OR episode_id IS NULL THEN
        RETURN jsonb_build_object('value', NULL, 'error', 'Invalid parameters', 'is_ok', false);
    END IF;

    SELECT SUM(step_reward) INTO total_reward
    FROM agent_trajectories
    WHERE agent_id = agent_id AND episode = episode_id;

    IF total_reward IS NULL THEN
        total_reward := 0.0;
    END IF;

    RETURN jsonb_build_object(
        'value', jsonb_build_object('total_reward', total_reward),
        'error', NULL,
        'is_ok', true
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN jsonb_build_object('value', NULL, 'error', SQLERRM, 'is_ok', false);
END;
$$ LANGUAGE plpgsql;
