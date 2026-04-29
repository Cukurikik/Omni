package rules.stylellm

default style_allowed = false

style_allowed {
    input.toxicity_score < 0.1
    input.target_style != "hate_speech"
    # Rego policy to ensure StyleLLM text transfers do not violate safety standards
}
