# OMNI Engine — GPU Access Control Policy (Rego/OPA)
# Domain: Fine-grained RBAC for training job GPU resource allocation

package omni.security.gpu_access

import future.keywords.in
import future.keywords.if
import future.keywords.contains

default allow := false

# Role hierarchy
role_hierarchy := {
    "admin": 100,
    "lead_researcher": 80,
    "researcher": 60,
    "engineer": 40,
    "viewer": 10
}

# GPU tier definitions
gpu_tiers := {
    "a100_80gb": {"vram_gb": 80, "min_role_level": 60, "max_concurrent": 4},
    "a100_40gb": {"vram_gb": 40, "min_role_level": 40, "max_concurrent": 8},
    "rtx_4090":  {"vram_gb": 24, "min_role_level": 40, "max_concurrent": 16},
    "rtx_3090":  {"vram_gb": 24, "min_role_level": 10, "max_concurrent": 32},
    "t4":        {"vram_gb": 16, "min_role_level": 10, "max_concurrent": 64}
}

# Main authorization rule
allow if {
    valid_user
    valid_action
    sufficient_role
    within_quota
    not blacklisted
}

# User validation
valid_user if {
    input.user.id != ""
    input.user.org != ""
    input.user.role in object.keys(role_hierarchy)
}

# Action validation
valid_action if {
    input.action in ["allocate", "release", "query", "list", "monitor"]
}

# Role-based access
sufficient_role if {
    input.action == "query"
}

sufficient_role if {
    input.action == "list"
}

sufficient_role if {
    input.action == "monitor"
    role_hierarchy[input.user.role] >= 40
}

sufficient_role if {
    input.action == "allocate"
    gpu_tier := gpu_tiers[input.resource.gpu_type]
    user_level := role_hierarchy[input.user.role]
    user_level >= gpu_tier.min_role_level
}

sufficient_role if {
    input.action == "release"
    role_hierarchy[input.user.role] >= 40
}

# Quota enforcement
within_quota if {
    input.action != "allocate"
}

within_quota if {
    input.action == "allocate"
    gpu_tier := gpu_tiers[input.resource.gpu_type]
    input.resource.current_allocated < gpu_tier.max_concurrent
    input.user.current_jobs < max_jobs_for_role(input.user.role)
}

# Max concurrent jobs per role
max_jobs_for_role(role) := 20 if { role == "admin" }
max_jobs_for_role(role) := 10 if { role == "lead_researcher" }
max_jobs_for_role(role) := 5 if { role == "researcher" }
max_jobs_for_role(role) := 3 if { role == "engineer" }
max_jobs_for_role(role) := 0 if { role == "viewer" }

# Blacklist check
blacklisted if {
    input.user.id in data.blacklisted_users
}

# Budget enforcement
budget_remaining := remaining if {
    allocated := input.user.budget_used
    limit := budget_limit_for_role(input.user.role)
    remaining := limit - allocated
}

budget_limit_for_role(role) := 10000.0 if { role == "admin" }
budget_limit_for_role(role) := 5000.0 if { role == "lead_researcher" }
budget_limit_for_role(role) := 2000.0 if { role == "researcher" }
budget_limit_for_role(role) := 500.0 if { role == "engineer" }
budget_limit_for_role(role) := 0.0 if { role == "viewer" }

# Detailed authorization response
authorization := response if {
    response := {
        "allowed": allow,
        "user": input.user.id,
        "role": input.user.role,
        "role_level": role_hierarchy[input.user.role],
        "action": input.action,
        "budget_remaining": budget_remaining,
        "reasons": denial_reasons
    }
}

# Collect denial reasons
denial_reasons contains "invalid_user" if { not valid_user }
denial_reasons contains "invalid_action" if { not valid_action }
denial_reasons contains "insufficient_role" if { not sufficient_role }
denial_reasons contains "quota_exceeded" if { not within_quota }
denial_reasons contains "blacklisted" if { blacklisted }
