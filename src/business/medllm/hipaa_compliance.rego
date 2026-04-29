package medllm.compliance

default is_compliant = false

is_compliant {
    input.anonymized == true
    input.data_type == "PHI"
    input.encryption_level >= 256
}

# OmniResult format mapped in Rego
omni_result = {
    "value": is_compliant,
    "error": null,
    "is_ok": true
}
