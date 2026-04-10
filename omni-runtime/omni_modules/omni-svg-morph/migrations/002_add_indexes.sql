-- omni-svg-morph Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_svg_morph_data_gin ON omni_svg_morph_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_svg_morph_metadata_gin ON omni_svg_morph_entities USING gin(metadata);