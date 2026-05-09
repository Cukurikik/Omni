-- OMNI Framework - SQLite Schema for KeyBERT Extraction Cache
-- Enables fast lookups for previously processed documents to save compute

CREATE TABLE IF NOT EXISTS keybert_cache (
    document_hash TEXT PRIMARY KEY,
    extracted_keywords TEXT NOT NULL, -- JSON array of keywords
    confidence_scores TEXT NOT NULL,  -- JSON array of scores
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_keybert_cache_time ON keybert_cache(processed_at);

-- Example Insert:
-- INSERT INTO keybert_cache (document_hash, extracted_keywords, confidence_scores, model_version)
-- VALUES ('a1b2c3d4...', '["finance", "market"]', '[0.95, 0.88]', 'keybert-base-v1');
