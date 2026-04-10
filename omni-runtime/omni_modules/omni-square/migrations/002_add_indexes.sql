-- omni-square Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_square_data_gin ON omni_square_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_square_metadata_gin ON omni_square_entities USING gin(metadata);