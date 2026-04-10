-- omni-crypto-usdc Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_crypto_usdc_data_gin ON omni_crypto_usdc_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_crypto_usdc_metadata_gin ON omni_crypto_usdc_entities USING gin(metadata);