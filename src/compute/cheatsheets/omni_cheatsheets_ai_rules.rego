# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Cheatsheets AI Rego Policy (OMNI Zero-Mock Implementation)
# Implements Data Sanitization capability validation.

package cheatsheets_ai.policy

# Determine if model inference can proceed
default allow_inference = false

# Validate payload size deterministically
allow_inference {
    input.payload_size_kb < 1024
    input.api_key_valid == true
    input.rate_limit_exceeded == false
    not contains_pii(input.prompt)
}

# Simple PII block abstraction (deterministic check)
contains_pii(prompt) {
    blocked_keywords := ["SSN", "Credit Card", "CVV"]
    some i
    contains(prompt, blocked_keywords[i])
}
