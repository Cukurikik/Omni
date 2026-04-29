package omni.security.kserve

default allow_inference = false

# Allow inference if the user has a valid API key with 'predict' scope
allow_inference {
    input.request.headers["Authorization"] == concat("Bearer ", input.valid_tokens[_].token)
    "predict" in input.valid_tokens[_].scopes
}

# Deny if requesting a model in the "restricted" namespace without admin roles
deny_inference {
    input.request.model_namespace == "restricted"
    not "admin" in input.valid_tokens[_].roles
}
