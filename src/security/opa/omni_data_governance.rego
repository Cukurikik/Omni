# OMNI Security — Open Policy Agent (OPA) Data Governance
package omni.governance

default allow = false

# Allow inference if data is not PII
allow {
    input.action == "inference"
    not contains_pii(input.payload)
}

# Allow fine-tuning only if data is anonymized and user is researcher
allow {
    input.action == "finetune"
    input.dataset.status == "anonymized"
    input.user.role == "researcher"
}

# Deny access to encrypted models without KMS token
deny[msg] {
    input.model.is_encrypted == true
    not input.kms_token
    msg := "KMS Token required for encrypted models."
}

# Helper rule to simulate PII detection
contains_pii(payload) {
    regex.match(`\b\d{3}-\d{2}-\d{4}\b`, payload) # SSN pattern
}
