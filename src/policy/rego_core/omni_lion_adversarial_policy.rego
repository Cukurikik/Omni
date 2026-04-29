package omni.security.lion

import future.keywords.in

default allow = false

# OPA Policy for Lion Adversarial Distillation Execution
allow {
    input.method == "POST"
    input.path == ["api", "distillation", "execute"]
    is_valid_researcher
    has_role("ml_engineer")
}

is_valid_researcher {
    # Simulating deterministic token validation
    input.token != ""
    input.token.issuer == "omni-ml-identity-server"
    input.token.clearance_level >= 3
}

has_role(role) {
    role in input.token.roles
}
