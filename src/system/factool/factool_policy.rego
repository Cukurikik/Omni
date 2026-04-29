package factool.policy

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.request.action == "scan_factuality"
    input.request.model != "unauthorized_model"
}
