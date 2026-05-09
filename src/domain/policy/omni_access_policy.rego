# omni_access_policy.rego — Open Policy Agent Policy
# Layer: Security / Domain
#
# Rego policy defining Attribute-Based Access Control (ABAC) and RBAC
# for OMNI Network Gateway APIs and Model Inference endpoints.

package omni.authz

default allow = false

# Allow if the user is a superadmin
allow {
    input.user.roles[_] == "superadmin"
}

# Allow inference if the user has the 'inference.execute' permission
# and their quota is not exhausted.
allow {
    input.action == "inference.execute"
    input.user.roles[_] == "researcher"
    input.user.quota_remaining > 0
}

# Allow modifying routing configurations if user belongs to the logistics domain
allow {
    input.action == "routing.optimize"
    input.user.department == "logistics"
}

# Restrict access to specific foundation models based on clearance level
allow {
    input.action == "inference.execute"
    input.resource.model_name == "omni-coco-lm-large"
    input.user.clearance_level >= 3
}

# Deny access from blacklisted IPs immediately
deny[msg] {
    some ip in data.blacklisted_ips
    input.request.source_ip == ip
    msg := "IP address is blacklisted"
}

# Require MFA for any administrative actions
deny[msg] {
    input.action == "system.configure"
    not input.user.mfa_authenticated
    msg := "MFA required for system configuration"
}
