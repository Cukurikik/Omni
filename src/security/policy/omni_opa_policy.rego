package omni.access.transformer

# Omni OPA Policy (Rego)
# Security & Policy Layer
# Defines zero-trust authorization logic for accessing heavily compute-bound
# Transformer inference clusters and model registries.

default allow = false

# Allow access if user is admin
allow {
    input.user.role == "admin"
}

# Allow inference execution if user has active quota and model is public
allow {
    input.action == "inference"
    input.resource.type == "model"
    input.resource.visibility == "public"
    input.user.quota_remaining > 0
}

# Allow fine-tuning only on proprietary datasets if the user belongs to the owning organization
allow {
    input.action == "fine_tune"
    input.resource.type == "dataset"
    input.resource.owner_org == input.user.org_id
}

# Restrict access to raw model weights unless user has explicit security clearance
allow {
    input.action == "download_weights"
    input.resource.type == "model"
    input.user.clearance_level >= input.resource.security_level
}

# Deny access from blacklisted IPs
deny {
    input.network.source_ip == data.blacklisted_ips[_]
}
