-- omni-threejs Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_threejs_data_gin ON omni_threejs_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_threejs_metadata_gin ON omni_threejs_entities USING gin(metadata);