-- omni-weaviate Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_weaviate_data_gin ON omni_weaviate_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_weaviate_metadata_gin ON omni_weaviate_entities USING gin(metadata);