package omni.security.llm

default allow = false

# Allow access to LLM inference if user has premium tier or is admin
allow {
    input.user.role == "admin"
}

allow {
    input.user.subscription_tier == "premium"
    input.request.model_type == "ghn3-hypernetwork"
}

allow {
    input.user.subscription_tier == "standard"
    input.request.model_type == "distilbert"
    input.request.tokens < 1000
}
