-- omni-faunadb Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_faunadb_data_gin ON omni_faunadb_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_faunadb_metadata_gin ON omni_faunadb_entities USING gin(metadata);