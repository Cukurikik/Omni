-- omni-timescaledb Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_timescaledb_data_gin ON omni_timescaledb_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_timescaledb_metadata_gin ON omni_timescaledb_entities USING gin(metadata);