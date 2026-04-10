-- omni-matter-js Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_matter_js_data_gin ON omni_matter_js_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_matter_js_metadata_gin ON omni_matter_js_entities USING gin(metadata);