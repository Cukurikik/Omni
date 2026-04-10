-- omni-paypal Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_paypal_data_gin ON omni_paypal_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_paypal_metadata_gin ON omni_paypal_entities USING gin(metadata);