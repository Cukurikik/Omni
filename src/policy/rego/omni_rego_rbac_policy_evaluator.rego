# OMNI MOTHER — SEMESTER 13 REMEDIATION
# Rego Language — Security & Policy Layer (OMNI Zero-Mock Implementation)
# Implements deterministic RBAC policy evaluation with role hierarchy resolution.
# Absorbs patterns from: github.com/open-policy-agent/opa

package omni.policy.rbac

# Role hierarchy: admin > editor > viewer
# Each role inherits permissions from roles below it.

default allow := false

# Role hierarchy mapping — exact role containment mathematics
role_hierarchy := {
    "admin":  {"admin", "editor", "viewer"},
    "editor": {"editor", "viewer"},
    "viewer": {"viewer"},
}

# Permission matrix — maps role to allowed operations on resources
permissions := {
    "viewer":  [{"action": "read",   "resource": "*"}],
    "editor":  [{"action": "read",   "resource": "*"},
                {"action": "write",  "resource": "*"},
                {"action": "update", "resource": "*"}],
    "admin":   [{"action": "read",   "resource": "*"},
                {"action": "write",  "resource": "*"},
                {"action": "update", "resource": "*"},
                {"action": "delete", "resource": "*"},
                {"action": "admin",  "resource": "*"}],
}

# Compute effective roles including inherited roles
effective_roles[role] {
    some assigned_role
    input.user.roles[_] == assigned_role
    role_hierarchy[assigned_role][role]
}

# Main authorization rule
allow {
    some role
    effective_roles[role]
    some perm
    permissions[role][_] == perm
    perm.action == input.action
    perm.resource == "*"
}

allow {
    some role
    effective_roles[role]
    some perm
    permissions[role][_] == perm
    perm.action == input.action
    perm.resource == input.resource
}

# Denial rules — explicit deny overrides allow
deny {
    input.user.suspended == true
}

deny {
    input.user.roles == null
}

# Final decision: allow AND NOT deny
authorized := allow == true
not_denied := not deny

result := {
    "allowed": authorized,
    "denied": deny,
    "effective_roles": effective_roles,
    "reason": reason,
}

reason := "Access granted" {
    authorized
    not_denied
}

reason := "User suspended" {
    deny
    input.user.suspended == true
}

reason := "No roles assigned" {
    deny
    input.user.roles == null
}

reason := "Insufficient permissions" {
    not authorized
    not deny
}
