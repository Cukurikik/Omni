package omni.authz

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.method == "GET"
    input.path == ["public", _]
}
