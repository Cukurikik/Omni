package omni.security.iam

import future.keywords.in

default is_authorized = false

# RBAC Logic for OMNI Distributed Compute Nodes

# A user is authorized if any of their roles grant the required permission
is_authorized {
    some role in input.user.roles
    permission_granted(role, input.resource, input.action)
}

# Role definitions and mapping
permission_granted(role, resource, action) {
    role_permissions := data.roles[role]
    some perm in role_permissions
    
    # Action Match
    perm.action == action
    
    # Resource Match (Support for exact match or wildcard)
    match_resource(perm.resource, resource)
}

match_resource(policy_res, request_res) {
    policy_res == request_res
}

match_resource(policy_res, request_res) {
    endswith(policy_res, "*")
    prefix := trim_suffix(policy_res, "*")
    startswith(request_res, prefix)
}

# Super Admin override mechanism
is_authorized {
    "omni-superadmin" in input.user.roles
}

# Explicit Deny Overrides (Highest Precedence)
deny[msg] {
    "suspicious_origin" in input.user.flags
    msg := "User origin flagged by intrusion detection system."
}

deny[msg] {
    input.resource == "system:kernel:allocator"
    input.user.mfa_verified == false
    msg := "MFA required for kernel level access."
}

# To combine allow/deny
final_decision {
    is_authorized
    count(deny) == 0
}
