-- omni-framer-motion Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_framer_motion_data_gin ON omni_framer_motion_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_framer_motion_metadata_gin ON omni_framer_motion_entities USING gin(metadata);