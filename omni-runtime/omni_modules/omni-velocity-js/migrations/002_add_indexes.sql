-- omni-velocity-js Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_velocity_js_data_gin ON omni_velocity_js_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_velocity_js_metadata_gin ON omni_velocity_js_entities USING gin(metadata);