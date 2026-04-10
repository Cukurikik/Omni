-- omni-canvas-turbo Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_canvas_turbo_data_gin ON omni_canvas_turbo_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_canvas_turbo_metadata_gin ON omni_canvas_turbo_entities USING gin(metadata);