package omni.auth

default allow = false

# Allow if user is admin
allow {
    input.user.role == "admin"
}

# Allow if user owns the requested model resource
allow {
    input.request.method == "POST"
    input.user.id == input.resource.owner_id
}

# Allow read-only access for guests on public models
allow {
    input.request.method == "GET"
    input.resource.visibility == "public"
}
