-- omni-linode-obj Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_linode_obj_data_gin ON omni_linode_obj_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_linode_obj_metadata_gin ON omni_linode_obj_entities USING gin(metadata);