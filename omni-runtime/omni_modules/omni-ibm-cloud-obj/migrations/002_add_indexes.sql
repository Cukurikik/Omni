-- omni-ibm-cloud-obj Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_ibm_cloud_obj_data_gin ON omni_ibm_cloud_obj_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_ibm_cloud_obj_metadata_gin ON omni_ibm_cloud_obj_entities USING gin(metadata);