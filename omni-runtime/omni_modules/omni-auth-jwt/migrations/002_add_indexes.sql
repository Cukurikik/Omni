-- omni-auth-jwt Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_auth_jwt_data_gin ON omni_auth_jwt_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_auth_jwt_metadata_gin ON omni_auth_jwt_entities USING gin(metadata);