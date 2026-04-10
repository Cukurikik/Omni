-- omni-braintree Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_braintree_data_gin ON omni_braintree_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_braintree_metadata_gin ON omni_braintree_entities USING gin(metadata);