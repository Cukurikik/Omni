-- omni-azure-blob Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_azure_blob_data_gin ON omni_azure_blob_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_azure_blob_metadata_gin ON omni_azure_blob_entities USING gin(metadata);