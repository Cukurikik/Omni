-- omni-vultr-obj Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_vultr_obj_data_gin ON omni_vultr_obj_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_vultr_obj_metadata_gin ON omni_vultr_obj_entities USING gin(metadata);