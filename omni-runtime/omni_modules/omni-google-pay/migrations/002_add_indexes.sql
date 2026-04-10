-- omni-google-pay Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_google_pay_data_gin ON omni_google_pay_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_google_pay_metadata_gin ON omni_google_pay_entities USING gin(metadata);