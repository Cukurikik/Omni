-- omni-aws-lambda Initial Migration
CREATE TABLE IF NOT EXISTS omni_aws_lambda_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_aws_lambda_status ON omni_aws_lambda_entities(status);
CREATE INDEX idx_omni_aws_lambda_created ON omni_aws_lambda_entities(created_at);