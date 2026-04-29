package rules.omnix

default is_culturally_safe = false

is_culturally_safe {
    input.toxicity_score < 0.1
    input.cultural_bias_score < 0.2
    # Rego policy for ensuring cross-lingual outputs don't violate cultural sensitivities
}
