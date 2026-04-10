-- omni-wow-js Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_wow_js_data_gin ON omni_wow_js_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_wow_js_metadata_gin ON omni_wow_js_entities USING gin(metadata);