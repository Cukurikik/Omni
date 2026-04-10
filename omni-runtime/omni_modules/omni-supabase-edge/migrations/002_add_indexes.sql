-- omni-supabase-edge Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_supabase_edge_data_gin ON omni_supabase_edge_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_supabase_edge_metadata_gin ON omni_supabase_edge_entities USING gin(metadata);