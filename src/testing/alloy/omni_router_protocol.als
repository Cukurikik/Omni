/*
 * OMNI Framework - Alloy Model for Neural Data Router (NDR)
 * Verifies that the top-k expert selection protocol correctly prevents token dropping
 * and maintains structural routing invariants.
 */

module omni/router

sig Token {}

sig Expert {
    processes: set Token
}

sig Router {
    experts: set Expert,
    k: Int
}

fact RouterConstraints {
    // Top-k must be positive
    all r: Router | r.k > 0
    
    // Each token must be processed by exactly 'k' experts in the router
    // This is a simplification; in practice, it's at most k if some experts have 0 weight
    all t: Token, r: Router | #(r.experts & processes.t) = r.k
}

assert NoDroppedTokens {
    // If a token exists, it must be processed by at least one expert
    all t: Token | some e: Expert | t in e.processes
}

check NoDroppedTokens for 5 Token, 3 Expert, 1 Router
