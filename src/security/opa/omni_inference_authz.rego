// OMNI Security — OPA Rego Policy for Inference Authorization
// Fine-grained access control for model inference endpoints.

package omni.inference.authz

import future.keywords.in
import future.keywords.if

default allow := false

# Roles definition
admin_roles := {"admin", "platform-admin", "ml-engineer"}
user_roles := {"developer", "researcher", "analyst"}
readonly_roles := {"viewer", "auditor"}

# Model tiers
production_models := {"omni-7b", "omni-13b", "omni-70b"}
staging_models := {"omni-7b-dev", "omni-13b-beta"}
experimental_models := {"omni-tiny", "omni-small", "omni-base"}

# Allow admin full access
allow if {
    input.user.role in admin_roles
}

# Allow users to inference on non-production models
allow if {
    input.user.role in user_roles
    input.action == "inference"
    not input.model_id in production_models
}

# Allow users production access with rate limit token
allow if {
    input.user.role in user_roles
    input.action == "inference"
    input.model_id in production_models
    input.user.has_production_access == true
    input.request.tokens_requested <= 4096
}

# Allow readonly roles to view metrics only
allow if {
    input.user.role in readonly_roles
    input.action in {"view_metrics", "view_logs", "list_models"}
}

# Block requests exceeding token limit
deny[msg] if {
    input.action == "inference"
    input.request.tokens_requested > 8192
    msg := sprintf("Token limit exceeded: requested %d > max 8192", [input.request.tokens_requested])
}

# Block unauthenticated requests
deny[msg] if {
    not input.user
    msg := "Authentication required"
}

# Rate limiting metadata
rate_limit := limit if {
    input.user.role in admin_roles
    limit := {"requests_per_minute": 1000, "tokens_per_minute": 100000}
}

rate_limit := limit if {
    input.user.role in user_roles
    limit := {"requests_per_minute": 100, "tokens_per_minute": 50000}
}

rate_limit := limit if {
    input.user.role in readonly_roles
    limit := {"requests_per_minute": 10, "tokens_per_minute": 0}
}
