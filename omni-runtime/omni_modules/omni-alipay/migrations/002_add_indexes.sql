-- omni-alipay Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_alipay_data_gin ON omni_alipay_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_alipay_metadata_gin ON omni_alipay_entities USING gin(metadata);