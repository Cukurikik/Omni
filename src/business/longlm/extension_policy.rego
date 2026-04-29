package omni.business.longlm

default allow_extension = false

# Rego policy for context window expansion limits
# Prevents OOM attacks by bounding context extensions

allow_extension {
    input.requested_context_length <= 128000
    input.available_vram_gb >= 40
}

allow_extension {
    input.user_tier == "enterprise"
    input.requested_context_length <= 512000
    input.available_vram_gb >= 80
}

omni_result = {
    "value": allow_extension,
    "error": null,
    "is_ok": true
}
