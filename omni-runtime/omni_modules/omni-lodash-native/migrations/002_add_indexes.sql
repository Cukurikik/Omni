-- omni-lodash-native Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_lodash_native_data_gin ON omni_lodash_native_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_lodash_native_metadata_gin ON omni_lodash_native_entities USING gin(metadata);