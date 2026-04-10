-- omni-bitpay Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_bitpay_data_gin ON omni_bitpay_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_bitpay_metadata_gin ON omni_bitpay_entities USING gin(metadata);