-- omni-spline-3d Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_spline_3d_data_gin ON omni_spline_3d_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_spline_3d_metadata_gin ON omni_spline_3d_entities USING gin(metadata);