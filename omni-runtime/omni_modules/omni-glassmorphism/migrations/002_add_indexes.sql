-- omni-glassmorphism Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_glassmorphism_data_gin ON omni_glassmorphism_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_glassmorphism_metadata_gin ON omni_glassmorphism_entities USING gin(metadata);