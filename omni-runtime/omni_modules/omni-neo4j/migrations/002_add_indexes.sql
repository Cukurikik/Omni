-- omni-neo4j Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_neo4j_data_gin ON omni_neo4j_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_neo4j_metadata_gin ON omni_neo4j_entities USING gin(metadata);