-- omni-parallax-core Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_parallax_core_data_gin ON omni_parallax_core_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_parallax_core_metadata_gin ON omni_parallax_core_entities USING gin(metadata);