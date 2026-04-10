-- omni-influxdb Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_influxdb_data_gin ON omni_influxdb_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_influxdb_metadata_gin ON omni_influxdb_entities USING gin(metadata);