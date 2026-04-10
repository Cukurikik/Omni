-- omni-supabase-storage Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_supabase_storage_data_gin ON omni_supabase_storage_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_supabase_storage_metadata_gin ON omni_supabase_storage_entities USING gin(metadata);