-- @omni-layer Business | @omni-source minimaxir/imgbeddings | @omni-lang SQL
-- @omni-description Image embedding store: relational schema for CLIP embedding
-- storage, similarity search caching, and collection management.

CREATE TABLE IF NOT EXISTS omni_image_collections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL UNIQUE,
    description     TEXT,
    embedding_dim   INT NOT NULL DEFAULT 512,
    model_name      VARCHAR(100) NOT NULL DEFAULT 'clip-vit-base',
    total_images    INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS omni_image_embeddings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id   UUID NOT NULL REFERENCES omni_image_collections(id) ON DELETE CASCADE,
    image_url       TEXT NOT NULL,
    image_hash      VARCHAR(64) NOT NULL,
    embedding       FLOAT8[] NOT NULL,
    metadata        JSONB DEFAULT '{}',
    file_size_bytes BIGINT,
    width           INT,
    height          INT,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(collection_id, image_hash)
);

CREATE INDEX IF NOT EXISTS idx_emb_collection ON omni_image_embeddings(collection_id);
CREATE INDEX IF NOT EXISTS idx_emb_hash ON omni_image_embeddings(image_hash);
CREATE INDEX IF NOT EXISTS idx_emb_metadata ON omni_image_embeddings USING GIN(metadata);

CREATE TABLE IF NOT EXISTS omni_similarity_cache (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash      VARCHAR(64) NOT NULL,
    collection_id   UUID NOT NULL REFERENCES omni_image_collections(id),
    result_ids      UUID[] NOT NULL,
    scores          FLOAT8[] NOT NULL,
    top_k           INT NOT NULL,
    cached_at       TIMESTAMP DEFAULT NOW(),
    expires_at      TIMESTAMP DEFAULT NOW() + INTERVAL '1 hour',
    UNIQUE(query_hash, collection_id, top_k)
);

CREATE TABLE IF NOT EXISTS omni_embedding_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id   UUID NOT NULL REFERENCES omni_image_collections(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending','processing','completed','failed')),
    total_images    INT NOT NULL DEFAULT 0,
    processed       INT NOT NULL DEFAULT 0,
    failed          INT NOT NULL DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- View: collection statistics
CREATE OR REPLACE VIEW omni_collection_stats AS
SELECT
    c.id, c.name, c.embedding_dim, c.model_name,
    COUNT(e.id) AS actual_images,
    AVG(e.file_size_bytes) AS avg_file_size,
    MIN(e.created_at) AS earliest_image,
    MAX(e.created_at) AS latest_image
FROM omni_image_collections c
LEFT JOIN omni_image_embeddings e ON c.id = e.collection_id
GROUP BY c.id;
