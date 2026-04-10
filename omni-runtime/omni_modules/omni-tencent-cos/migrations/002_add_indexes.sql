-- omni-tencent-cos Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_tencent_cos_data_gin ON omni_tencent_cos_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_tencent_cos_metadata_gin ON omni_tencent_cos_entities USING gin(metadata);