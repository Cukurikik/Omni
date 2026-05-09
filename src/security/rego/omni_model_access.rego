# OMNI Security Layer — Rego Policy for Model Access Control
# OPA (Open Policy Agent) policies for OMNI inference and deployment.

package omni.security.model_access

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# Default deny all
default allow := false

# Role definitions
admin_roles := {"admin", "ml-engineer-lead", "platform-admin"}
deploy_roles := {"admin", "ml-engineer-lead", "ml-engineer", "devops"}
inference_roles := {"admin", "ml-engineer", "data-scientist", "developer", "api-user"}
readonly_roles := {"admin", "ml-engineer", "data-scientist", "viewer"}

# Allow inference requests
allow if {
    input.action == "infer"
    input.user.role in inference_roles
    valid_api_key
    within_rate_limit
    model_is_deployed
}

# Allow model deployment
allow if {
    input.action == "deploy"
    input.user.role in deploy_roles
    model_is_ready
    valid_deployment_target
    not model_already_deployed_to_env
}

# Allow model management (create, update, delete)
allow if {
    input.action in {"create", "update"}
    input.user.role in deploy_roles
}

allow if {
    input.action == "delete"
    input.user.role in admin_roles
    model_is_not_deployed
}

# Read-only access
allow if {
    input.action in {"list", "get", "metrics"}
    input.user.role in readonly_roles
}

# Validation helpers
valid_api_key if {
    input.api_key != ""
    not input.api_key in blocked_keys
}

blocked_keys := {"revoked-key-001", "expired-key-002"}

within_rate_limit if {
    input.user.requests_this_minute < rate_limits[input.user.role]
}

rate_limits := {
    "admin": 1000,
    "ml-engineer-lead": 500,
    "ml-engineer": 200,
    "data-scientist": 100,
    "developer": 60,
    "api-user": 30,
    "viewer": 10,
}

model_is_deployed if {
    input.model.status == "deployed"
}

model_is_ready if {
    input.model.status == "ready"
}

model_is_not_deployed if {
    input.model.status != "deployed"
}

valid_deployment_target if {
    input.target.environment in {"staging", "production", "canary"}
    input.target.region in {"us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"}
    input.target.replicas > 0
    input.target.replicas <= max_replicas[input.target.environment]
}

max_replicas := {
    "staging": 3,
    "canary": 2,
    "production": 100,
}

model_already_deployed_to_env if {
    some deployment in input.existing_deployments
    deployment.environment == input.target.environment
    deployment.status == "active"
}

# Data sensitivity checks
deny_sensitive_data if {
    contains(input.request.prompt, "password")
}

deny_sensitive_data if {
    regex.match(`\b\d{3}-\d{2}-\d{4}\b`, input.request.prompt)  # SSN pattern
}

deny_sensitive_data if {
    regex.match(`\b\d{16}\b`, input.request.prompt)  # Credit card pattern
}

# Audit logging
audit_event := event if {
    event := {
        "timestamp": time.now_ns(),
        "user": input.user.id,
        "action": input.action,
        "model": input.model.name,
        "allowed": allow,
        "reason": audit_reason,
    }
}

audit_reason := "authorized" if { allow }
audit_reason := "unauthorized_role" if { not allow; not input.user.role in inference_roles }
audit_reason := "rate_limited" if { not allow; not within_rate_limit }
audit_reason := "model_not_ready" if { not allow; not model_is_deployed }
