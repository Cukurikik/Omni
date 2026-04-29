package rules.mustango

default is_generation_allowed = false

is_generation_allowed {
    input.contains_copyrighted_melody == false
    input.prompt_safety_check == "passed"
    # Rego policy to prevent direct reproduction of copyrighted music
}
