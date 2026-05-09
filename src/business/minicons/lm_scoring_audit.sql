-- @omni-layer Business | @omni-source kanishkamisra/minicons
-- @omni-description LM scoring audit trail in SQL: tables for tracking surprisal
-- computations, perplexity metrics, and model comparison results.
-- @omni-lang SQL | @omni-batch 16 | @omni-semester 16

CREATE TABLE IF NOT EXISTS lm_scoring_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(256) NOT NULL,
    model_version VARCHAR(64),
    vocab_size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(32) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS token_surprisals (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID REFERENCES lm_scoring_sessions(session_id),
    sequence_id VARCHAR(128) NOT NULL,
    position INTEGER NOT NULL,
    token_id INTEGER NOT NULL,
    token_text VARCHAR(256),
    surprisal_bits DOUBLE PRECISION NOT NULL,
    log_probability DOUBLE PRECISION NOT NULL,
    rank_in_vocab INTEGER,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sequence_metrics (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID REFERENCES lm_scoring_sessions(session_id),
    sequence_id VARCHAR(128) NOT NULL UNIQUE,
    n_tokens INTEGER NOT NULL,
    mean_surprisal DOUBLE PRECISION NOT NULL,
    perplexity DOUBLE PRECISION NOT NULL,
    total_log_likelihood DOUBLE PRECISION NOT NULL,
    entropy DOUBLE PRECISION,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_comparisons (
    id BIGSERIAL PRIMARY KEY,
    sequence_id VARCHAR(128) NOT NULL,
    model_a_session UUID REFERENCES lm_scoring_sessions(session_id),
    model_b_session UUID REFERENCES lm_scoring_sessions(session_id),
    ppl_a DOUBLE PRECISION NOT NULL,
    ppl_b DOUBLE PRECISION NOT NULL,
    delta_ppl DOUBLE PRECISION GENERATED ALWAYS AS (ppl_a - ppl_b) STORED,
    winner VARCHAR(16) GENERATED ALWAYS AS (CASE WHEN ppl_a < ppl_b THEN 'model_a' ELSE 'model_b' END) STORED,
    compared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_surprisals_session ON token_surprisals(session_id);
CREATE INDEX idx_surprisals_sequence ON token_surprisals(sequence_id);
CREATE INDEX idx_metrics_session ON sequence_metrics(session_id);
CREATE INDEX idx_comparisons_sequence ON model_comparisons(sequence_id);
