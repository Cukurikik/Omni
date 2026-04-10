-- omni-pinecone Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_pinecone_data_gin ON omni_pinecone_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_pinecone_metadata_gin ON omni_pinecone_entities USING gin(metadata);