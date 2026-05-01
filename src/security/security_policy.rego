# OMNI Engine — Security Policy (Rego)
# Implements: Role-Based Access Control and Data Filtering
# Layer: Security & Policy Layer

package omni.security

default allow = false

# Allow if user is admin
allow {
    input.user.role == "admin"
}

# Allow if user owns the resource
allow {
    input.user.id == input.resource.owner_id
    input.action == "read"
}

# OmniResult format returned as JSON mapping
result = {
    "is_ok": true,
    "value": {
        "allowed": allow,
        "reason": "Policy evaluated successfully"
    }
} {
    allow
}

result = {
    "is_ok": false,
    "error": "Access denied by policy constraint"
} {
    not allow
}

# Data filtering: Only return public fields unless admin
visible_fields[field] {
    fields := ["id", "name", "public_profile"]
    field := fields[_]
}

visible_fields[field] {
    input.user.role == "admin"
    fields := ["id", "name", "public_profile", "billing_info", "private_keys"]
    field := fields[_]
}
