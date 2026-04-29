package omni_tree

import "core:math"

entropy :: proc(probs: []f64) -> f64 {
    e := 0.0
    for p in probs {
        if p > 0.0 {
            e -= p * math.log2(p)
        }
    }
    return e
}

gini_impurity :: proc(probs: []f64) -> f64 {
    g := 1.0
    for p in probs {
        g -= p * p
    }
    return g
}
