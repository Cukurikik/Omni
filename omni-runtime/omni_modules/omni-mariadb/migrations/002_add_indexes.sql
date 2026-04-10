-- omni-mariadb Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mariadb_data_gin ON omni_mariadb_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_mariadb_metadata_gin ON omni_mariadb_entities USING gin(metadata);