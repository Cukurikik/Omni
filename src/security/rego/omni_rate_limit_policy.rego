# OMNI Security — OPA Rate Limiting Policy
package omni.ratelimit

default allow = true

# Deny if Free Tier user exceeds 1000 tokens per minute
deny[msg] {
    input.user.tier == "free"
    input.metrics.tokens_last_minute > 1000
    msg := "Rate limit exceeded for Free Tier."
}

# Deny if Enterprise user exceeds account hard cap
deny[msg] {
    input.user.tier == "enterprise"
    input.metrics.tokens_last_minute > input.user.hard_cap_tpm
    msg := "Enterprise hard cap exceeded."
}

# Always allow Admin bypass
allow {
    input.user.role == "admin"
}
