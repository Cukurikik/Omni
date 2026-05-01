# OMNI Engine — Rego OPA Policy
# Layer: Security
# Implements: Open Policy Agent strict resource access rules

package omni.authz

default allow = false

# Allow if user is admin
allow {
    input.user.role == "admin"
}

# Allow if user is editor and action is write
allow {
    input.user.role == "editor"
    input.request.action == "write"
    input.request.resource_type == "document"
}

# Allow if user is viewer and action is read
allow {
    input.user.role == "viewer"
    input.request.action == "read"
    input.request.resource_type == "document"
}

# Omni Monadic Result simulation via structured output
result = {
    "is_ok": allow,
    "value": "Access Granted",
    "error": "Access Denied by OPA Policy"
}
