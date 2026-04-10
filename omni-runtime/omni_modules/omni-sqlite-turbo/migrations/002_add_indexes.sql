-- omni-sqlite-turbo Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_sqlite_turbo_data_gin ON omni_sqlite_turbo_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_sqlite_turbo_metadata_gin ON omni_sqlite_turbo_entities USING gin(metadata);