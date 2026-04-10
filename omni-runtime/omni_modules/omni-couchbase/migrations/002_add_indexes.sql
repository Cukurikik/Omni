-- omni-couchbase Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_couchbase_data_gin ON omni_couchbase_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_couchbase_metadata_gin ON omni_couchbase_entities USING gin(metadata);