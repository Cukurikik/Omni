module OmniStateModel

/*
 * Omni Alloy Formal Verification.
 * Ensures state machine integrity across the UAST.
 */

sig Node {
    connections: set Node
}

sig Network {
    nodes: set Node
}

// Invariant: Network cannot contain disconnected islands
fact Connectivity {
    all n1, n2: Node | n1 in n2.^connections
}

// Assert no self-connections in routing tables
assert NoSelfRouting {
    no n: Node | n in n.connections
}

check NoSelfRouting for 10
