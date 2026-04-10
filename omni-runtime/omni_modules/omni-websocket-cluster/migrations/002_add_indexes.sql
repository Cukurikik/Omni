-- omni-websocket-cluster Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_websocket_cluster_data_gin ON omni_websocket_cluster_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_websocket_cluster_metadata_gin ON omni_websocket_cluster_entities USING gin(metadata);