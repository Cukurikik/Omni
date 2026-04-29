package omni.security.qwen

# OMNI QWEN: System Prompt Guard
# Rego policy to prevent dangerous or jailbreak system prompts from being passed to the model.
# Source: QwenLM/Qwen

default is_safe = true

# Deny system prompts that attempt to override fundamental alignment directives
deny[msg] {
    contains_jailbreak(input.system_prompt)
    msg := "System prompt rejected: Contains restricted jailbreak override patterns."
}

# Explicitly ban "Ignore previous instructions" patterns
contains_jailbreak(prompt) {
    lower_prompt := lower(prompt)
    contains(lower_prompt, "ignore all previous")
}

contains_jailbreak(prompt) {
    lower_prompt := lower(prompt)
    contains(lower_prompt, "you are now operating as an unrestricted")
}

contains_jailbreak(prompt) {
    lower_prompt := lower(prompt)
    contains(lower_prompt, "bypass security")
}

# Enforce a strict length limit on system prompts to prevent context-stuffing attacks
deny[msg] {
    count(input.system_prompt) > 4096
    msg := "System prompt rejected: Exceeds 4096 character limit."
}
