package omni.security.kiln

# OMNI Rego Security Layer: Kiln Evaluation Access
# Controls access to sensitive RLHF datasets and evaluation metrics.

default allow = false

# Allow AI Researchers to read evaluation metrics
allow {
    input.action == "read"
    input.resource.type == "evaluation_report"
    input.user.roles[_] == "ai-researcher"
}

# Allow Evaluators to submit new evaluations
allow {
    input.action == "submit"
    input.resource.type == "evaluation_result"
    input.user.roles[_] == "evaluator"
}

# Deny modification of historical evaluations (Immutability rule)
deny[msg] {
    input.action == "update"
    input.resource.type == "evaluation_result"
    msg = "Integrity Violation: Evaluation results are immutable once committed."
}

# Deny access to PII-flagged datasets unless authorized
deny[msg] {
    input.action == "read"
    input.resource.contains_pii == true
    not input.user.clearance_level == "high"
    msg = "Access Denied: Insufficient clearance to read PII-flagged evaluation datasets."
}
