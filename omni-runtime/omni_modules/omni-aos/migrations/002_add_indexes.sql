-- omni-aos Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_aos_data_gin ON omni_aos_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_aos_metadata_gin ON omni_aos_entities USING gin(metadata);