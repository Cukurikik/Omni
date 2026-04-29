// Omni Diagram of Thought (Alloy)
// Formal Verification Layer: Structural verification of DAG reasoning constraints.

sig ReasoningNode {
    dependsOn: set ReasoningNode
}

// Acyclic property: No node can depend on itself directly or transitively
fact AcyclicDAG {
    no n: ReasoningNode | n in n.^dependsOn
}

// Ensure there is at least one root node (no dependencies)
fact RootExists {
    some n: ReasoningNode | no n.dependsOn
}

assert DAGIsSound {
    all n: ReasoningNode | n not in n.^dependsOn
}

check DAGIsSound for 5
