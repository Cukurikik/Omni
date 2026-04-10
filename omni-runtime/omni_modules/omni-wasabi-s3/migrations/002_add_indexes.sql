-- omni-wasabi-s3 Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_wasabi_s3_data_gin ON omni_wasabi_s3_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_wasabi_s3_metadata_gin ON omni_wasabi_s3_entities USING gin(metadata);