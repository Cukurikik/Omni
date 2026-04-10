-- omni-rive-animation Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_rive_animation_data_gin ON omni_rive_animation_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_rive_animation_metadata_gin ON omni_rive_animation_entities USING gin(metadata);