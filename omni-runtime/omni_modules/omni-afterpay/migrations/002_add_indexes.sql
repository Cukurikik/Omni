-- omni-afterpay Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_afterpay_data_gin ON omni_afterpay_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_afterpay_metadata_gin ON omni_afterpay_entities USING gin(metadata);