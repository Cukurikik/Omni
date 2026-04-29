package rules.llmplanning

default plan_is_safe = false

plan_is_safe {
    not contains_destructive_action(input.actions)
    input.estimated_cost < 100
    # Rego constraints preventing LLM planners from executing catastrophic commands
}

contains_destructive_action(actions) {
    actions[_] == "rm -rf /"
}
