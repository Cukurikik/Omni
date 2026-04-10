-- omni-scaleway-obj Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_scaleway_obj_data_gin ON omni_scaleway_obj_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_scaleway_obj_metadata_gin ON omni_scaleway_obj_entities USING gin(metadata);