-- omni-mollie Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mollie_data_gin ON omni_mollie_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mollie_metadata_gin ON omni_mollie_entities USING gin(metadata);