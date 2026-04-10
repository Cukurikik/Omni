-- omni-stripe Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_stripe_data_gin ON omni_stripe_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_stripe_metadata_gin ON omni_stripe_entities USING gin(metadata);