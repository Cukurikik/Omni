package omni.security.transformers

# OMNI TRANSFORMERS: License Tracker & Policy
# Rego policy to prevent deploying models with restrictive licenses into commercial environments.
# Source: huggingface/transformers

default deployment_allowed = false

# Allow deployment if the target environment is 'research'
deployment_allowed {
    input.environment == "research"
}

# Allow deployment in 'commercial' if the license permits
deployment_allowed {
    input.environment == "commercial"
    is_commercial_friendly(input.model_metadata.license)
}

# Explicitly Deny commercial use for restricted models
deny[msg] {
    input.environment == "commercial"
    not is_commercial_friendly(input.model_metadata.license)
    msg := sprintf("Deployment blocked: Model '%v' has restrictive license '%v' not suitable for commercial use.", [input.model_metadata.name, input.model_metadata.license])
}

# Helper to define what constitutes a commercial-friendly license
is_commercial_friendly(license) {
    allowed_licenses := {"Apache-2.0", "MIT", "BSD-3-Clause", "OpenRAIL-M"}
    allowed_licenses[_] == license
}
