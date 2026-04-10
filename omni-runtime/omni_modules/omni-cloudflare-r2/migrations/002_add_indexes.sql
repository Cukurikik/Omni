-- omni-cloudflare-r2 Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cloudflare_r2_data_gin ON omni_cloudflare_r2_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_cloudflare_r2_metadata_gin ON omni_cloudflare_r2_entities USING gin(metadata);