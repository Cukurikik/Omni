-- omni-webpack-killer Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_webpack_killer_data_gin ON omni_webpack_killer_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_webpack_killer_metadata_gin ON omni_webpack_killer_entities USING gin(metadata);