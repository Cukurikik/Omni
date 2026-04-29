; Omni Expert System in CLIPS
; Forward-chaining rules for diagnostic logic

(defrule check-layer-violation
    (engine-request (source ?src) (target ?tgt))
    (test (eq ?src "interface"))
    (test (eq ?tgt "system"))
    =>
    (assert (omni-error "CRITICAL: Interface layer cannot directly access System layer. Use Domain Bridge."))
)

(defrule validate-monadic-compliance
    (code-block (type ?type) (has-result-monad FALSE))
    =>
    (assert (omni-error "VIOLATION: Missing Result<T, E> handling in code block."))
)
