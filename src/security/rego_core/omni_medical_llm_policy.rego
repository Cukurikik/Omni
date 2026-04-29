# Omni Medical LLM Policy (Rego/OPA)
# Security Layer: Safety policy for medical LLM inference requests.
# Ref: BIDS-Xu-Lab/Me-LLaMA

package omni.medical.policy

default allow_inference = false

allow_inference {
    input.user.role == "physician"
    input.request.model_family == "me-llama"
    not contains_pii(input.request.prompt)
}

contains_pii(prompt) {
    regex.match(`\b\d{3}-\d{2}-\d{4}\b`, prompt)
}

contains_pii(prompt) {
    regex.match(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`, prompt)
}
