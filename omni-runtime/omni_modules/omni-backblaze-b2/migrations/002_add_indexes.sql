-- omni-backblaze-b2 Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_backblaze_b2_data_gin ON omni_backblaze_b2_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_backblaze_b2_metadata_gin ON omni_backblaze_b2_entities USING gin(metadata);