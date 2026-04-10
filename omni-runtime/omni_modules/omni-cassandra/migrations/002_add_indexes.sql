-- omni-cassandra Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cassandra_data_gin ON omni_cassandra_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cassandra_metadata_gin ON omni_cassandra_entities USING gin(metadata);