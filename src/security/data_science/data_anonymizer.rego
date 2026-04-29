package omni.data.security

# OMNI DATA SCIENCE: PII Anonymizer Policy
# Rego rules to detect and enforce masking of PII (Personally Identifiable Information) in datasets before model training.
# Source: CodeCutTech/Data-science

default needs_masking = false

# Define sensitive fields
sensitive_fields := {"email", "ssn", "credit_card", "phone_number", "address"}

# Determine if a dataset column needs masking
needs_masking {
    input.operation == "READ_DATASET"
    column_name := input.column_metadata.name
    is_sensitive(column_name)
}

is_sensitive(col_name) {
    # Check if the column name implies PII
    sensitive_fields[_] == lower(col_name)
}

# Advanced heuristic: check if data classification tags identify PII
needs_masking {
    input.operation == "READ_DATASET"
    input.column_metadata.tags[_] == "PII"
}

# Rule defining what masking strategy to apply
masking_strategy = strategy {
    needs_masking
    column_name := input.column_metadata.name
    strategy := determine_strategy(column_name)
}

determine_strategy(col) = "HASH_SHA256" {
    col == "email"
}

determine_strategy(col) = "REDACT_FULL" {
    col == "ssn"
}

determine_strategy(col) = "REDACT_PARTIAL_LAST_4" {
    col == "credit_card"
}

# Default strategy for other PII
determine_strategy(col) = "MASK_ASTERISK" {
    not col == "email"
    not col == "ssn"
    not col == "credit_card"
}
