package omni.gateway.authz

# OMNI MOTHER: Open Policy Agent for Gateway API

default allow_api = false

allow_api {
    input.token == "valid_omni_token"
    input.path == "/api/v1/inference"
}
