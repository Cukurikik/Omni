package omni.semester14.batch8.tonic

# OMNI Rego Policy for TonicValidate Metrics
# Enforces strict data governance on validation scores

default allow_metric_save = false

# Maximum allowed variance for a validation run
max_allowed_variance := 0.05

# Require minimum bounds for acceptable metric saves
min_lower_bound := 0.70

allow_metric_save {
    input.metric_name != ""
    input.data.mean >= 0
    input.data.mean <= 1
    input.data.variance <= max_allowed_variance
    input.data.lowerBound >= min_lower_bound
    
    # Ensure standard errors are not impossibly small (floating point drift)
    input.data.variance > 0.000001
}

deny[msg] {
    input.data.mean < 0
    msg := "OMNI_POLICY_ERR: Mean cannot be negative"
}

deny[msg] {
    input.data.variance > max_allowed_variance
    msg := sprintf("OMNI_POLICY_ERR: Variance %v exceeds limit %v", [input.data.variance, max_allowed_variance])
}
