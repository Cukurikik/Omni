package rules.adaptiveclassifier

default meets_confidence_threshold = false

meets_confidence_threshold {
    input.classification_confidence >= 0.85
    input.model_drift_score <= 0.1
}

omni_result = {
    "value": meets_confidence_threshold,
    "error": null,
    "is_ok": true
}
