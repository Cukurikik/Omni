-- omni-kafka-stream Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_kafka_stream_data_gin ON omni_kafka_stream_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_kafka_stream_metadata_gin ON omni_kafka_stream_entities USING gin(metadata);