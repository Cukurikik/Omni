# @omni-layer Security | @omni-lang Rego (Open Policy Agent) | @omni-batch 17
# @omni-description Inference access policy: OPA Rego rules for model access
# control, rate limiting, data classification, and audit compliance.

package omni.inference.policy

import future.keywords.if
import future.keywords.in
import future.keywords.contains

default allow := false

# Core access decision
allow if {
    valid_user
    valid_model
    within_quota
    data_classification_ok
    not blacklisted
}

# User validation
valid_user if {
    input.user.id != ""
    input.user.role in {"admin", "developer", "data_scientist", "analyst"}
    input.user.authenticated == true
}

# Model access control
valid_model if {
    model := data.models[input.model_id]
    model.status == "active"
    input.user.role in model.allowed_roles
}

# Rate limiting
within_quota if {
    quota := data.quotas[input.user.id]
    quota.used < quota.daily_limit
}

within_quota if {
    not data.quotas[input.user.id]  # No quota entry = unlimited
}

# Data classification
data_classification_ok if {
    input.data_classification in {"public", "internal"}
}

data_classification_ok if {
    input.data_classification == "confidential"
    input.user.role in {"admin", "data_scientist"}
    input.user.clearance_level >= 3
}

data_classification_ok if {
    input.data_classification == "restricted"
    input.user.role == "admin"
    input.user.clearance_level >= 5
}

# Blacklist check
blacklisted if {
    input.user.id in data.blacklist
}

# Audit logging decision
audit_required if {
    input.data_classification in {"confidential", "restricted"}
}

audit_required if {
    input.model_id in data.high_risk_models
}

# Inference cost estimation
estimated_cost := cost if {
    model := data.models[input.model_id]
    cost := model.cost_per_token * input.max_tokens
}

# Violations report
violations contains msg if {
    not valid_user
    msg := "Invalid or unauthenticated user"
}

violations contains msg if {
    not valid_model
    msg := sprintf("Model %v not accessible", [input.model_id])
}

violations contains msg if {
    not within_quota
    msg := "Daily quota exceeded"
}

violations contains msg if {
    not data_classification_ok
    msg := sprintf("Insufficient clearance for %v data", [input.data_classification])
}

violations contains msg if {
    blacklisted
    msg := "User is blacklisted"
}

# Summary
decision := {
    "allow": allow,
    "violations": violations,
    "audit_required": audit_required,
    "estimated_cost": estimated_cost,
}
