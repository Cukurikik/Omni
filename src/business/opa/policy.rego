package omni.authz

default allow = false

allow {
    input.user == "admin"
}
