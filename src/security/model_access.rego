package omni.mlops.authz

default allow = false

allow {
    input.user.role == "data_scientist"
    input.action == "read"
    input.resource.type == "model"
}

allow {
    input.user.role == "ml_engineer"
    input.resource.type == "model"
}
