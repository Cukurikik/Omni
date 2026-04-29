package omni.authz.microservice

import future.keywords.in

default allow = false

# OPA Microservice Authorization for Omni Event Bus
allow {
    input.method == "POST"
    input.path == ["api", "events", "publish"]
    is_valid_jwt
    has_role("event_publisher")
}

is_valid_jwt {
    # Simulating deterministic token validation
    input.token != ""
    input.token.issuer == "omni-identity-server"
}

has_role(role) {
    role in input.token.roles
}
