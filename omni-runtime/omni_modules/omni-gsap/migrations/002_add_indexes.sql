-- omni-gsap Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_gsap_data_gin ON omni_gsap_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_gsap_metadata_gin ON omni_gsap_entities USING gin(metadata);