-- omni-bcrypt-native Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_bcrypt_native_data_gin ON omni_bcrypt_native_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_bcrypt_native_metadata_gin ON omni_bcrypt_native_entities USING gin(metadata);