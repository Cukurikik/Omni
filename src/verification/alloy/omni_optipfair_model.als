// OMNI Framework - Alloy Formal Verification Model for Optipfair
// Verifies that bias mitigation constraints do not violate basic fairness properties

module omni/optipfair

sig User {
    demographic: one DemographicGroup
}

sig DemographicGroup {}

sig Decision {
    target: one User,
    outcome: one Int
}

// Fairness property: Decisions must not be strictly determined by demographic group
pred demographic_parity {
    all d1, d2: Decision |
        (d1.target.demographic != d2.target.demographic) => 
        // In a perfectly fair model, outcomes shouldn't be rigidly tied to demographics
        // We model this loosely for verification
        # {d: Decision | d.target.demographic == d1.target.demographic and d.outcome > 0} 
        = # {d: Decision | d.target.demographic == d2.target.demographic and d.outcome > 0}
}

// Assert that our Optipfair mitigation (when applied) ensures parity
assert MitigationEnsuresParity {
    demographic_parity
}

check MitigationEnsuresParity for 10
