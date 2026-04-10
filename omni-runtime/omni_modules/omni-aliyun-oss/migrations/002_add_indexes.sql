-- omni-aliyun-oss Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_aliyun_oss_data_gin ON omni_aliyun_oss_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_aliyun_oss_metadata_gin ON omni_aliyun_oss_entities USING gin(metadata);