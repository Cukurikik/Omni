-- omni-p5-js Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_p5_js_data_gin ON omni_p5_js_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_p5_js_metadata_gin ON omni_p5_js_entities USING gin(metadata);