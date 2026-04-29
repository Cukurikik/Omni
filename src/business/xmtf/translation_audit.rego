package rules.xmtf

default translation_approved = false

translation_approved {
    input.bleu_score >= 0.4
    input.contains_profanity == false
}

omni_result = {
    "value": translation_approved,
    "error": null,
    "is_ok": true
}
