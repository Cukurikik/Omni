-- omni-heroku-dynos Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_heroku_dynos_data_gin ON omni_heroku_dynos_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_heroku_dynos_metadata_gin ON omni_heroku_dynos_entities USING gin(metadata);