-- omni-mongodb Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mongodb_data_gin ON omni_mongodb_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mongodb_metadata_gin ON omni_mongodb_entities USING gin(metadata);