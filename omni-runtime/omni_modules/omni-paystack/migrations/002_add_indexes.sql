-- omni-paystack Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_paystack_data_gin ON omni_paystack_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_paystack_metadata_gin ON omni_paystack_entities USING gin(metadata);