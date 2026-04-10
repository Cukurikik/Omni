-- omni-mojs Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mojs_data_gin ON omni_mojs_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mojs_metadata_gin ON omni_mojs_entities USING gin(metadata);