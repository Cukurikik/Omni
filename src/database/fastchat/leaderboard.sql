-- OMNI FASTCHAT: Chat Arena Leaderboard
-- SQL schema storing Elo ratings, match histories, and model stats.
-- Source: lm-sys/FastChat

CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(128) UNIQUE NOT NULL,
    organization VARCHAR(128),
    license VARCHAR(64),
    elo_rating DOUBLE PRECISION DEFAULT 1000.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS arena_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_a_id UUID NOT NULL REFERENCES models(id),
    model_b_id UUID NOT NULL REFERENCES models(id),
    winner_id UUID REFERENCES models(id), -- NULL if tie or both bad
    is_tie BOOLEAN DEFAULT FALSE,
    is_both_bad BOOLEAN DEFAULT FALSE,
    turn_count INT NOT NULL,
    user_id VARCHAR(64), -- Hashed or anonymized
    match_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for Elo recalculations
CREATE INDEX idx_matches_models ON arena_matches(model_a_id, model_b_id);
CREATE INDEX idx_models_elo ON models(elo_rating DESC);

-- View: Leaderboard
CREATE OR REPLACE VIEW v_arena_leaderboard AS
SELECT 
    RANK() OVER (ORDER BY elo_rating DESC) as rank,
    model_name,
    organization,
    ROUND(elo_rating::numeric, 1) as elo,
    (SELECT COUNT(*) FROM arena_matches WHERE model_a_id = m.id OR model_b_id = m.id) as match_count
FROM models m
WHERE (SELECT COUNT(*) FROM arena_matches WHERE model_a_id = m.id OR model_b_id = m.id) > 100;
