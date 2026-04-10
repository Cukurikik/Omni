-- omni-aws-lambda Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_aws_lambda_data_gin ON omni_aws_lambda_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_aws_lambda_metadata_gin ON omni_aws_lambda_entities USING gin(metadata);