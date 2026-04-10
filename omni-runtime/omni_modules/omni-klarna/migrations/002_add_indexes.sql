-- omni-klarna Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_klarna_data_gin ON omni_klarna_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_klarna_metadata_gin ON omni_klarna_entities USING gin(metadata);