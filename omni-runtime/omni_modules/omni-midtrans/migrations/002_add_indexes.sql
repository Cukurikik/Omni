-- omni-midtrans Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_midtrans_data_gin ON omni_midtrans_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_midtrans_metadata_gin ON omni_midtrans_entities USING gin(metadata);