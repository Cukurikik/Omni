-- omni-razorpay Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_razorpay_data_gin ON omni_razorpay_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_razorpay_metadata_gin ON omni_razorpay_entities USING gin(metadata);