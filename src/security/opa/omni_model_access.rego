# OMNI Framework - Open Policy Agent (OPA) Rules
# Fine-grained access control for specific LLM models

package omni.model.access

default allow = false

# Allow access if the user is an admin
allow {
    input.user.role == "admin"
}

# Allow developers access to development models
allow {
    input.user.role == "developer"
    startswith(input.model.name, "dev-")
}

# Allow enterprise users access to production models if they have active subscription
allow {
    input.user.role == "enterprise"
    not startswith(input.model.name, "dev-")
    input.tenant.subscription_status == "active"
}

# Deny access to classified models unless user has clearance
deny {
    input.model.classification == "secret"
    input.user.clearance != "top-secret"
}
