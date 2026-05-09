-- @omni-layer Business | @omni-source lucidrains/improving-transformers-world-model-for-rl | @omni-lang SQL
-- @omni-description RL experiment store: relational schema for RL training runs,
-- trajectory storage, reward tracking, and hyperparameter logging.

CREATE TABLE IF NOT EXISTS omni_rl_experiments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    algorithm       VARCHAR(50) NOT NULL CHECK(algorithm IN ('ppo','sac','dreamer','world_model','muzero')),
    environment     VARCHAR(100) NOT NULL,
    status          VARCHAR(20) DEFAULT 'created' CHECK(status IN ('created','training','completed','failed','cancelled')),
    gamma           FLOAT8 NOT NULL DEFAULT 0.99,
    learning_rate   FLOAT8 NOT NULL DEFAULT 3e-4,
    horizon         INT NOT NULL DEFAULT 100,
    d_state         INT NOT NULL DEFAULT 64,
    d_action        INT NOT NULL DEFAULT 8,
    total_steps     BIGINT DEFAULT 0,
    best_reward     FLOAT8,
    created_at      TIMESTAMP DEFAULT NOW(),
    completed_at    TIMESTAMP
);

CREATE TABLE IF NOT EXISTS omni_rl_trajectories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id   UUID NOT NULL REFERENCES omni_rl_experiments(id) ON DELETE CASCADE,
    episode         INT NOT NULL,
    total_reward    FLOAT8 NOT NULL,
    discounted_return FLOAT8 NOT NULL,
    n_steps         INT NOT NULL,
    avg_value       FLOAT8,
    max_reward_step FLOAT8,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_traj_experiment ON omni_rl_trajectories(experiment_id);
CREATE INDEX IF NOT EXISTS idx_traj_reward ON omni_rl_trajectories(total_reward DESC);

CREATE TABLE IF NOT EXISTS omni_rl_checkpoints (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id   UUID NOT NULL REFERENCES omni_rl_experiments(id),
    step            BIGINT NOT NULL,
    reward          FLOAT8 NOT NULL,
    checkpoint_path TEXT NOT NULL,
    model_size_mb   FLOAT8,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(experiment_id, step)
);

CREATE TABLE IF NOT EXISTS omni_rl_hyperparams (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id   UUID NOT NULL REFERENCES omni_rl_experiments(id),
    param_name      VARCHAR(100) NOT NULL,
    param_value     TEXT NOT NULL,
    param_type      VARCHAR(20) DEFAULT 'float',
    UNIQUE(experiment_id, param_name)
);

-- View: experiment summary with trajectory stats
CREATE OR REPLACE VIEW omni_rl_experiment_summary AS
SELECT
    e.id, e.name, e.algorithm, e.environment, e.status,
    COUNT(t.id) AS total_episodes,
    AVG(t.total_reward) AS avg_reward,
    MAX(t.total_reward) AS best_episode_reward,
    AVG(t.n_steps) AS avg_episode_length,
    e.total_steps
FROM omni_rl_experiments e
LEFT JOIN omni_rl_trajectories t ON e.id = t.experiment_id
GROUP BY e.id;
