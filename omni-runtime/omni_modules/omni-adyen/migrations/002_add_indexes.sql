-- omni-adyen Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_adyen_data_gin ON omni_adyen_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_adyen_metadata_gin ON omni_adyen_entities USING gin(metadata);