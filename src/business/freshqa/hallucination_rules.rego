package rules.freshqa

default is_hallucination = true

is_hallucination = false {
    input.factual_consistency_score > 0.85
    input.source_citations_valid == true
    # Rego policy to classify strict hallucinations in FreshQA tasks
}
