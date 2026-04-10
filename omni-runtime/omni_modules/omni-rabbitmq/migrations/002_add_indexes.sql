-- omni-rabbitmq Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_rabbitmq_data_gin ON omni_rabbitmq_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_rabbitmq_metadata_gin ON omni_rabbitmq_entities USING gin(metadata);