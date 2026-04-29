package rules.mlsecops

default allow_inference = false

allow_inference {
    input.model_provenance_verified == true
    input.cve_count == 0
    input.adversarial_robustness > 0.90
    # Rego policy firewall for ML model deployment
}
