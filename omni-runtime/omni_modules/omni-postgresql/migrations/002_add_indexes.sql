-- omni-postgresql Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_postgresql_data_gin ON omni_postgresql_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_postgresql_metadata_gin ON omni_postgresql_entities USING gin(metadata);