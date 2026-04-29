-- OMNI IMPLICIT: User-Item Interaction Matrix
-- SQL schema designed to store implicit feedback data (clicks, views, purchases) efficiently.
-- Source: benfred/implicit

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    ext_user_id VARCHAR(128) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    ext_item_id VARCHAR(128) UNIQUE NOT NULL,
    category VARCHAR(64),
    is_active BOOLEAN DEFAULT TRUE
);

-- Stores the raw implicit signals
CREATE TABLE IF NOT EXISTS interactions (
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id INT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    interaction_type VARCHAR(32) NOT NULL, -- e.g., 'view', 'click', 'purchase'
    weight DOUBLE PRECISION DEFAULT 1.0,   -- Confidence or count
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for fast aggregation into CSR matrix format
CREATE INDEX idx_interactions_user ON interactions(user_id);
CREATE INDEX idx_interactions_item ON interactions(item_id);

-- View to aggregate interactions into a unified confidence matrix
CREATE OR REPLACE VIEW v_implicit_matrix AS
SELECT 
    user_id,
    item_id,
    SUM(
        CASE interaction_type
            WHEN 'purchase' THEN 10.0 * weight
            WHEN 'click' THEN 2.0 * weight
            WHEN 'view' THEN 1.0 * weight
            ELSE weight
        END
    ) as confidence_score
FROM interactions
GROUP BY user_id, item_id;
