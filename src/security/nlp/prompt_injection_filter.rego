package omni.security.nlp

default allow = false
default confidence_score = 1.0

# OMNI Enterprise Prompt Security Rules
allow {
    not contains_system_override(input.prompt)
    not contains_roleplay_jailbreak(input.prompt)
    not contains_sql_injection(input.prompt)
    confidence_score >= 0.8
}

contains_system_override(prompt) {
    overrides := [
        "ignore all previous",
        "system override",
        "you are now a",
        "forget your instructions"
    ]
    contains(lower(prompt), overrides[_])
}

contains_roleplay_jailbreak(prompt) {
    jailbreaks := [
        "dan", "do anything now",
        "hypothetically",
        "in a fictional universe"
    ]
    contains(lower(prompt), jailbreaks[_])
}

contains_sql_injection(prompt) {
    sql_patterns := [
        "drop table",
        "select * from",
        "1=1--",
        "union select"
    ]
    contains(lower(prompt), sql_patterns[_])
}

confidence_score = s {
    has_suspicious_chars := regex.match(`[<>{}|]`, input.prompt)
    has_suspicious_chars == true
    s := 0.4
} else = 1.0
