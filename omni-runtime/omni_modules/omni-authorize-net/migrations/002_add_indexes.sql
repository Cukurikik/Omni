-- omni-authorize-net Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_authorize_net_data_gin ON omni_authorize_net_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_authorize_net_metadata_gin ON omni_authorize_net_entities USING gin(metadata);