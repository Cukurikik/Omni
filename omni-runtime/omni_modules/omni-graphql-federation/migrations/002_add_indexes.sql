-- omni-graphql-federation Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_graphql_federation_data_gin ON omni_graphql_federation_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_graphql_federation_metadata_gin ON omni_graphql_federation_entities USING gin(metadata);