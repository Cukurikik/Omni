-- omni-anime-js Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_anime_js_data_gin ON omni_anime_js_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_anime_js_metadata_gin ON omni_anime_js_entities USING gin(metadata);