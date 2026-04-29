package rules.awesomerag

default is_grounded = false

is_grounded {
    input.similarity_to_source > 0.85
    input.hallucination_score < 0.1
    # Rego policy enforcing strict factual grounding for RAG-generated answers
}
