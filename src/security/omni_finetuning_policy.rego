# OMNI Engine — Fine-Tuning Access Control Policy
# Absorbed: All 30 repos (security layer)
# Domain: OPA/Rego RBAC for fine-tuning resources

package omni.finetuning.access

import rego.v1

default allow := false

# Role definitions
roles := {
    "admin":      {"permissions": ["create", "read", "update", "delete", "publish", "manage_gpu"]},
    "ml_engineer": {"permissions": ["create", "read", "update", "publish"]},
    "researcher":  {"permissions": ["create", "read"]},
    "viewer":      {"permissions": ["read"]},
}

# GPU quota per role (hours per month)
gpu_quotas := {
    "admin":       {"A100": 1000, "H100": 500, "V100": 2000},
    "ml_engineer": {"A100": 200,  "H100": 100, "V100": 500},
    "researcher":  {"A100": 50,   "H100": 20,  "V100": 100},
    "viewer":      {"A100": 0,    "H100": 0,   "V100": 0},
}

# Method access restrictions
method_access := {
    "admin":       ["lora", "sorsa", "full_ft", "dreambooth", "ctc_asr", "flow_tts",
                    "sam_decoder", "text_to_video", "booster"],
    "ml_engineer": ["lora", "sorsa", "dreambooth", "ctc_asr", "flow_tts", "sam_decoder"],
    "researcher":  ["lora", "sorsa"],
    "viewer":      [],
}

# Allow if user has permission for action
allow if {
    some role in input.user.roles
    role_perms := roles[role].permissions
    input.action in role_perms
}

# GPU quota check
gpu_quota_ok if {
    some role in input.user.roles
    quota := gpu_quotas[role][input.gpu_type]
    input.requested_hours <= quota - input.used_hours
}

# Method access check
method_allowed if {
    some role in input.user.roles
    allowed_methods := method_access[role]
    input.method in allowed_methods
}

# Cost limit enforcement
cost_within_limit if {
    input.estimated_cost_usd <= input.user.cost_limit_usd
}

# Combined authorization
authorize if {
    allow
    gpu_quota_ok
    method_allowed
    cost_within_limit
}

# Denial reasons
deny_reasons contains reason if {
    not allow
    reason := "insufficient_permissions"
}

deny_reasons contains reason if {
    not gpu_quota_ok
    reason := "gpu_quota_exceeded"
}

deny_reasons contains reason if {
    not method_allowed
    reason := "method_not_allowed_for_role"
}

deny_reasons contains reason if {
    not cost_within_limit
    reason := "cost_limit_exceeded"
}

# Data sensitivity classification
sensitive_methods := ["booster", "pii_ner"]

requires_audit if {
    input.method in sensitive_methods
}

requires_encryption if {
    input.dataset_contains_pii == true
}
