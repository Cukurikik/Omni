-- OMNI Database Layer: ALICE EconML Causal Experiments
-- DDL for storing rigorous causal inference estimations and A/B test metadata.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS causal_experiments (
    experiment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name VARCHAR(100) NOT NULL,
    hypothesis TEXT NOT NULL,
    treatment_variable VARCHAR(100) NOT NULL,
    outcome_variable VARCHAR(100) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS causal_estimations (
    estimation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID NOT NULL REFERENCES causal_experiments(experiment_id) ON DELETE CASCADE,
    estimator_model VARCHAR(100) NOT NULL, -- e.g., 'DoubleMachineLearning', 'CausalForest'
    average_treatment_effect NUMERIC(10, 6) NOT NULL,
    lower_confidence_bound NUMERIC(10, 6) NOT NULL,
    upper_confidence_bound NUMERIC(10, 6) NOT NULL,
    p_value NUMERIC(6, 5) NOT NULL,
    sample_size INT NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for high performance filtering of significant effects
CREATE INDEX idx_causal_effect ON causal_estimations(average_treatment_effect);
CREATE INDEX idx_causal_significance ON causal_estimations(p_value) WHERE p_value < 0.05;

-- Analytics View: Rapid retrieval of successful experiments
CREATE OR REPLACE VIEW v_significant_experiments AS
SELECT 
    e.project_name,
    e.treatment_variable,
    e.outcome_variable,
    c.average_treatment_effect,
    c.p_value
FROM causal_experiments e
JOIN causal_estimations c ON e.experiment_id = c.experiment_id
WHERE c.p_value < 0.05 
  AND c.lower_confidence_bound * c.upper_confidence_bound > 0; -- Zero is not in the confidence interval
