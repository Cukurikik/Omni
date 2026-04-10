-- omni-vercel-edge Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_vercel_edge_data_gin ON omni_vercel_edge_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_vercel_edge_metadata_gin ON omni_vercel_edge_entities USING gin(metadata);