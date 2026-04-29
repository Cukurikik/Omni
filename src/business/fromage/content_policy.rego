package rules.fromage

default content_safe = false

content_safe {
    input.nsfw_score < 0.1
    input.contains_pii == false
}

omni_result = {
    "value": content_safe,
    "error": null,
    "is_ok": true
}
