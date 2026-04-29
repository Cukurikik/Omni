# Omni Anchoring Budget Policy (Rego/OPA)
# Security Layer: Budget enforcement for LLM pipeline execution.
# Ref: AnchoringAI/anchoring-ai
package omni.anchoring.budget
default allow_execution = false
allow_execution {
    input.budget.remaining > 0
    input.request.estimated_tokens * input.request.rate <= input.budget.remaining
}
