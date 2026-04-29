package omni.business.localrag

default allow = false

# Rego policy for LocalRAG document access control
# OmniResult schema wrapper implicitly applied in evaluation engine

allow {
    input.user.role == "admin"
}

allow {
    input.user.department == input.document.classification
    input.document.clearance_level <= input.user.clearance_level
}

omni_result = {
    "value": allow,
    "error": null,
    "is_ok": true
}
