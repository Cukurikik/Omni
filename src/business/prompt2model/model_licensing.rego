package rules.prompt2model

default allow_commercial_use = false

allow_commercial_use {
    input.base_model_license == "apache-2.0"
    input.dataset_license == "mit"
    # Rego policy ensuring generated models are legally compliant
}
