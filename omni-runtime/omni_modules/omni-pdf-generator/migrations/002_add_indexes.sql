-- omni-pdf-generator Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_pdf_generator_data_gin ON omni_pdf_generator_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_pdf_generator_metadata_gin ON omni_pdf_generator_entities USING gin(metadata);