package rbac.mace.mobile

# OMNI Security Layer: MACE Mobile Auth (Rego)
# Strict authorization for edge devices requesting model graph updates.

default allow = false

# Device must provide a valid hardware signature and be active
allow {
    input.method == "POST"
    input.path == "/api/mace/model/update"
    is_valid_device(input.device_id, input.hardware_sig)
    input.device_status == "active"
}

# Admin override
allow {
    input.user.roles[_] == "admin"
}

is_valid_device(id, sig) {
    # Emulate signature verification mapping
    id != ""
    sig != ""
    startswith(sig, "SHA256-")
}

# Rate limit prevention (Policy logic)
deny {
    input.rate_limit.requests_per_minute > 60
    not input.user.roles[_] == "admin"
}
