package rbac.marqo.index

# OMNI Security Layer: Marqo Index Access Control (Rego)
# Strict authorization policies for vector database modifications.

default allow = false

# Allow reads if user has viewer role or higher
allow {
    input.method == "GET"
    input.user.roles[_] == "viewer"
}

allow {
    input.method == "GET"
    input.user.roles[_] == "editor"
}

# Allow writes/updates only if user is editor or admin, AND the index belongs to their tenant
allow {
    input.method == "POST"
    input.user.roles[_] == "editor"
    input.resource.tenant_id == input.user.tenant_id
}

allow {
    input.method == "PUT"
    input.user.roles[_] == "editor"
    input.resource.tenant_id == input.user.tenant_id
}

# Admins can do anything
allow {
    input.user.roles[_] == "admin"
}

# Block all access if the origin IP is not in the VPC CIDR
deny {
    not net.cidr_contains("10.0.0.0/16", input.request.client_ip)
    not input.user.roles[_] == "admin"
}
