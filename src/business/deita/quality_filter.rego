package deita.quality

default meets_quality_threshold = false

meets_quality_threshold {
    input.instruction_length >= 10
    input.response_length >= 20
    input.complexity_score >= 0.75
}

omni_result = {
    "value": meets_quality_threshold,
    "error": null,
    "is_ok": true
}
