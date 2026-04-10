-- omni-scrollreveal Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_scrollreveal_data_gin ON omni_scrollreveal_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_scrollreveal_metadata_gin ON omni_scrollreveal_entities USING gin(metadata);