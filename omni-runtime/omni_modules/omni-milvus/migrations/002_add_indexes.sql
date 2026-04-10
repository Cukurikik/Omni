-- omni-milvus Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_milvus_data_gin ON omni_milvus_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_milvus_metadata_gin ON omni_milvus_entities USING gin(metadata);