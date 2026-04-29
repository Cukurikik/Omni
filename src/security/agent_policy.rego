package omni.agent.policy

default can_execute = false

can_execute {
    input.agent.role == "coder"
    input.task.type == "code_generation"
}

can_execute {
    input.agent.role == "researcher"
    input.task.type == "literature_review"
}
