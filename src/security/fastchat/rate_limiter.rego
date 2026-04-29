package omni.security.fastchat

# OMNI FASTCHAT: Arena Rate Limiter Policy
# Rego rules to prevent API abuse in the public Chatbot Arena.
# Source: lm-sys/FastChat

default allow_request = false

# Allow request if user hasn't exceeded the RPM (Requests Per Minute) limit
allow_request {
    input.endpoint == "/v1/chat/completions"
    not is_rate_limited(input.user_ip, input.user_tier)
}

# Define Tier Limits (Mocked logic, in reality this queries a Redis counter)
is_rate_limited(ip, tier) {
    tier == "free"
    input.current_rpm > 10
}

is_rate_limited(ip, tier) {
    tier == "premium"
    input.current_rpm > 100
}

# Global circuit breaker: Halt all free tier traffic if cluster load is critical
deny[msg] {
    input.cluster_status == "critical_load"
    input.user_tier == "free"
    msg := "Arena is currently under heavy load. Free tier access is temporarily paused."
}
