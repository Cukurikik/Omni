-- omni-date-fns Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_date_fns_data_gin ON omni_date_fns_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_date_fns_metadata_gin ON omni_date_fns_entities USING gin(metadata);