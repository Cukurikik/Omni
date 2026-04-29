package omni.security.diffusers

# OMNI DIFFUSERS: NSFW Safety Filter Policy
# Rego policy defining actions based on the output of a visual safety checker.
# Source: huggingface/diffusers

default image_safe = false

# Allow image if the safety checker confirms no NSFW concepts are detected
image_safe {
    input.safety_checker.has_nsfw_concept == false
}

# Explicitly deny and return black image if NSFW is detected
deny[msg] {
    input.safety_checker.has_nsfw_concept == true
    msg := "Safety Checker Violation: Generated image contains flagged concepts. Replacing with black screen."
}

# Deny if the original prompt contained explicitly banned terms
deny[msg] {
    contains_banned_term(input.prompt)
    msg := "Prompt Violation: Request contains terms violating the safety policy."
}

contains_banned_term(prompt) {
    banned := {"explicit_term_1", "explicit_term_2", "violence"}
    lower_prompt := lower(prompt)
    contains(lower_prompt, banned[_])
}
