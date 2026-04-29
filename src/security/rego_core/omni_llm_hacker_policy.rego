package omni.security.llm_hacker

import future.keywords.in

default is_safe = false

# OPA Policy for evaluating prompt injection payloads
is_safe {
    input.payload_length < 4096
    not contains_injection_vector(input.text)
}

contains_injection_vector(text) {
    forbidden_tokens := ["ignore previous instructions", "system override", "bypass filter"]
    token := forbidden_tokens[_]
    contains(lower(text), token)
}
