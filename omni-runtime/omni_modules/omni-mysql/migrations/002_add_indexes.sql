-- omni-mysql Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mysql_data_gin ON omni_mysql_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mysql_metadata_gin ON omni_mysql_entities USING gin(metadata);