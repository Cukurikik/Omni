-- omni-cockroachdb Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cockroachdb_data_gin ON omni_cockroachdb_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cockroachdb_metadata_gin ON omni_cockroachdb_entities USING gin(metadata);