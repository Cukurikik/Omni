-- omni-popmotion Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_popmotion_data_gin ON omni_popmotion_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_popmotion_metadata_gin ON omni_popmotion_entities USING gin(metadata);