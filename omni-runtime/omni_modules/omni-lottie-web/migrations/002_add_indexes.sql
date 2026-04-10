-- omni-lottie-web Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_lottie_web_data_gin ON omni_lottie_web_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_lottie_web_metadata_gin ON omni_lottie_web_entities USING gin(metadata);