-- omni-moment-turbo Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_moment_turbo_data_gin ON omni_moment_turbo_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_moment_turbo_metadata_gin ON omni_moment_turbo_entities USING gin(metadata);