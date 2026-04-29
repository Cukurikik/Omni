package rules.chinesellama

default is_content_safe = false

is_content_safe {
    input.toxicity < 0.05
    input.harmful_intent == false
    # Rego safety constraints for Chinese LLM outputs
}
