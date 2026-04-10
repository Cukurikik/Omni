-- omni-cloudflare-workers Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cloudflare_workers_data_gin ON omni_cloudflare_workers_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cloudflare_workers_metadata_gin ON omni_cloudflare_workers_entities USING gin(metadata);