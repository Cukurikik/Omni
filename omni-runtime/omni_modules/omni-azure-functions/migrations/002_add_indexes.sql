-- omni-azure-functions Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_azure_functions_data_gin ON omni_azure_functions_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_azure_functions_metadata_gin ON omni_azure_functions_entities USING gin(metadata);