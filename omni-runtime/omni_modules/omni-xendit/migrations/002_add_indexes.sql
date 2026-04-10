-- omni-xendit Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_xendit_data_gin ON omni_xendit_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_xendit_metadata_gin ON omni_xendit_entities USING gin(metadata);