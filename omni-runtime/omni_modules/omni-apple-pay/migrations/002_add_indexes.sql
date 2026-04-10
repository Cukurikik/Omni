-- omni-apple-pay Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_apple_pay_data_gin ON omni_apple_pay_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_apple_pay_metadata_gin ON omni_apple_pay_entities USING gin(metadata);