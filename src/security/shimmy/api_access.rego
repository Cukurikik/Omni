package omni.security.shimmy

# OMNI Rego Security Layer: Shimmy API Access
# Rate limiting and model access authorization for the Rust OpenAI-compatible server.

default allow = false

# Validate API token structure (Mocking structure check)
token_valid {
    startswith(input.headers["Authorization"], "Bearer omni-")
}

# Allow general models for verified users
allow {
    token_valid
    input.action == "chat_completion"
    input.model == "llama-3-8b-instruct"
}

# Restrict Enterprise/Heavy models to Enterprise accounts
allow {
    token_valid
    input.action == "chat_completion"
    input.model == "mixtral-8x22b"
    input.user.tier == "enterprise"
}

# Deny if rate limit exceeded (Quota check policy)
deny[msg] {
    input.quota.requests_per_minute > 600
    not input.user.tier == "enterprise"
    msg = "Rate limit exceeded: 600 RPM maximum for standard tier."
}

# Prevent hot-swapping models unless Admin
deny[msg] {
    input.action == "load_model"
    not input.user.roles[_] == "omni-cluster-admin"
    msg = "Access Denied: Only administrators can execute hot model swaps on Shimmy server."
}
