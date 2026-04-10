-- omni-digitalocean-spaces Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_digitalocean_spaces_data_gin ON omni_digitalocean_spaces_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_digitalocean_spaces_metadata_gin ON omni_digitalocean_spaces_entities USING gin(metadata);