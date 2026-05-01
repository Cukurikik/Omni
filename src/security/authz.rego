# OMNI Security Layer — Policy-as-code authorization engine.
# Language: Rego (OPA) (Security Layer)
# Fine-grained RBAC/ABAC with audit logging.

package omni.authz

import future.keywords.in
import future.keywords.if
import future.keywords.contains

default allow := false

# Role hierarchy
role_hierarchy := {
    "super_admin": ["admin", "editor", "viewer"],
    "admin": ["editor", "viewer"],
    "editor": ["viewer"],
    "viewer": [],
}

effective_roles[role] {
    some assigned_role in input.user.roles
    role := assigned_role
}

effective_roles[role] {
    some assigned_role in input.user.roles
    some inherited in role_hierarchy[assigned_role]
    role := inherited
}

# Resource-based permissions
resource_permissions := {
    "orders": {
        "read": ["viewer", "editor", "admin"],
        "create": ["editor", "admin"],
        "update": ["editor", "admin"],
        "delete": ["admin"],
    },
    "products": {
        "read": ["viewer", "editor", "admin"],
        "create": ["admin"],
        "update": ["editor", "admin"],
        "delete": ["admin"],
    },
    "users": {
        "read": ["admin"],
        "create": ["super_admin"],
        "update": ["admin"],
        "delete": ["super_admin"],
    },
    "analytics": {
        "read": ["editor", "admin"],
    },
}

# Main authorization rule
allow if {
    some role in effective_roles
    role in resource_permissions[input.resource][input.action]
}

# IP whitelist for admin actions
allow if {
    input.action in ["delete", "create"]
    input.resource == "users"
    input.client_ip in data.admin_whitelist_ips
}

# Rate limiting metadata
rate_limit := limit if {
    some role in effective_roles
    limits := {
        "viewer": 100,
        "editor": 500,
        "admin": 2000,
        "super_admin": 10000,
    }
    limit := limits[role]
}

# Audit decision
audit_entry := {
    "user": input.user.id,
    "resource": input.resource,
    "action": input.action,
    "allowed": allow,
    "roles": effective_roles,
    "timestamp": time.now_ns(),
}

# Data-level row filtering
row_filter[filter] if {
    input.resource == "orders"
    "viewer" in effective_roles
    not "admin" in effective_roles
    filter := {"customer_id": input.user.id}
}

row_filter[filter] if {
    input.resource == "orders"
    "admin" in effective_roles
    filter := {}
}

# Field masking for sensitive data
masked_fields contains field if {
    input.resource == "users"
    not "admin" in effective_roles
    field := "email"
}

masked_fields contains field if {
    input.resource == "users"
    not "super_admin" in effective_roles
    field := "ssn"
}
