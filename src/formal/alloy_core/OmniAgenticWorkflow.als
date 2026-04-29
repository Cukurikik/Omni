// Omni Agentic Workflow Alloy Specification
// Formal modeling of agentic state transitions.

sig Agent {
    state: one AgentState
}

abstract sig AgentState {}
one sig Idle, Thinking, Acting, Finished extends AgentState {}

sig Workflow {
    active_agent: lone Agent
}

// Ensure an agent cannot be acting without being in a workflow
fact {
    all a: Agent | a.state = Acting implies some w: Workflow | w.active_agent = a
}

// Transition logic
pred transition[a: Agent, s1, s2: AgentState] {
    a.state = s1
    // Abstract transition constraints
}

assert NoActingWithoutWorkflow {
    all a: Agent | a.state = Acting implies some w: Workflow | w.active_agent = a
}

check NoActingWithoutWorkflow for 5
