-- omni-firebase-native Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_firebase_native_data_gin ON omni_firebase_native_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_firebase_native_metadata_gin ON omni_firebase_native_entities USING gin(metadata);