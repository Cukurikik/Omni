-- OMNI Database Layer: SQLFlow Model Registry
-- Relational tracking of compiled machine learning models

CREATE TABLE IF NOT EXISTS sqlflow_models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    hyperparameters JSONB NOT NULL DEFAULT '{}',
    training_status VARCHAR(50) NOT NULL CHECK (training_status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_name ON sqlflow_models(model_name);
CREATE INDEX idx_training_status ON sqlflow_models(training_status);

-- Store predictions audit log
CREATE TABLE IF NOT EXISTS sqlflow_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES sqlflow_models(model_id) ON DELETE CASCADE,
    input_features JSONB NOT NULL,
    output_result JSONB NOT NULL,
    execution_time_ms INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prediction_model ON sqlflow_predictions(model_id);
