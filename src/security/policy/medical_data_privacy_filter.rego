# OMNI MOTHER SYSTEM - SECURITY LAYER
# Medical Data Privacy Filter (Open Policy Agent)
# Evaluates Attribute-Based Access Control (ABAC) and HIPAA-compliant data masking policies for Multi-Agent Medical NLP Systems.
# Absorbed from: SOLVE-Med

package omni.security.medical_privacy

import future.keywords.in

# Default deny all requests
default allow = false

# Allow access if the user is the assigned physician and the record is active
allow {
    input.action == "read"
    input.resource.type == "patient_record"
    
    # Ensure user has the 'physician' role
    "physician" in input.user.roles
    
    # Ensure physician is assigned to this specific patient
    input.user.id == input.resource.assigned_physician_id
}

# Allow AI Agents to access anonymized/de-identified data ONLY
allow {
    input.action == "analyze"
    input.resource.type == "patient_record"
    
    # Ensure the requester is an authorized AI SLM/LLM Agent
    "medical_ai_agent" in input.user.roles
    
    # Strict check: The data MUST be marked as de-identified
    input.resource.is_deidentified == true
}

# ---------------------------------------------------------
# PII (Personally Identifiable Information) Redaction Policy
# ---------------------------------------------------------

# Defines which fields must be redacted when a non-physician views the record
default needs_redaction = false

needs_redaction {
    # If the user is not the direct physician, redact PII
    not "physician" in input.user.roles
}

# The mask_data rule outputs the secure version of the payload
mask_data[key] = value {
    not needs_redaction
    input.resource.data[key] = value
}

mask_data[key] = value {
    needs_redaction
    input.resource.data[key] = raw_value
    
    # Apply masking logic based on field keys
    value := apply_mask(key, raw_value)
}

# Helper function to evaluate masking per field type
apply_mask(key, val) = "***REDACTED***" {
    sensitive_keys := {"ssn", "name", "phone", "address"}
    key in sensitive_keys
}

# Mask Date of Birth to Year only (HIPAA Safe Harbor pattern)
apply_mask("dob", val) = year {
    # Assuming dob format is YYYY-MM-DD
    year := substring(val, 0, 4)
}

# Return untouched value for non-sensitive keys
apply_mask(key, val) = val {
    sensitive_keys := {"ssn", "name", "phone", "address", "dob"}
    not key in sensitive_keys
}
