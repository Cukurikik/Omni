package omni.authz

default allow = false

# Allow system admins full access
allow {
    input.user.role == "system_admin"
}

# Allow compute nodes to pull tasks
allow {
    input.user.role == "compute_node"
    input.action == "pull_task"
    input.resource.layer == "compute"
}

# Allow interface nodes to read metrics
allow {
    input.user.role == "interface_node"
    input.action == "read_metrics"
}

# Deny all cross-layer unauthorized writes
deny {
    input.action == "write"
    input.user.layer != input.resource.layer
}
