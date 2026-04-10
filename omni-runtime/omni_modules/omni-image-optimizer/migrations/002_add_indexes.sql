-- omni-image-optimizer Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_image_optimizer_data_gin ON omni_image_optimizer_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_image_optimizer_metadata_gin ON omni_image_optimizer_entities USING gin(metadata);