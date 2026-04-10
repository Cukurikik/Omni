-- omni-redis Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_redis_data_gin ON omni_redis_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_redis_metadata_gin ON omni_redis_entities USING gin(metadata);