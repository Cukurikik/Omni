package omni.security.network

default allow = false

# Zero-Trust Principles:
# 1. Identity must be verified for all intra-system RPCs
# 2. Hardware limits must be respected per request

# Allow traffic only if JWT is valid, signature matches, and target layer is allowed
allow {
    valid_jwt
    allowed_layer_access
    within_rate_limits
}

# Verify JWT structure and signing (RSA-256 for OMNI Network)
valid_jwt {
    [valid, header, payload] := io.jwt.decode_verify(
        input.token,
        {"cert": data.public_keys[input.kid], "aud": "omni-cluster"}
    )
    valid == true
}

# Cross-layer constraints (UI cannot talk to System directly)
allowed_layer_access {
    source_layer := input.source_layer
    target_layer := input.target_layer

    # UI can only talk to Interface and Domain
    source_layer == "ui"
    target_layer == "interface"
}

allowed_layer_access {
    source_layer := input.source_layer
    target_layer := input.target_layer

    # Domain can talk to Compute and Concurrency
    source_layer == "domain"
    target_layer == "compute"
}

allowed_layer_access {
    source_layer := input.source_layer
    target_layer := input.target_layer

    # Concurrency can talk to System
    source_layer == "concurrency"
    target_layer == "system"
}

# Hardware and Rate Limit rules
within_rate_limits {
    input.payload_size_mb <= 5.0
    input.requests_per_second <= 100
}

# Deny specifically known malicious patterns or SQLi attempts in metadata
deny[msg] {
    regex.match(`(?i)(UNION SELECT|DROP TABLE|OR 1=1)`, input.metadata.query)
    msg := "SQL Injection pattern detected in network metadata"
}

deny[msg] {
    input.target_layer == "system"
    input.source_layer != "concurrency"
    msg := "Direct access to System layer is strictly prohibited by non-concurrency layers"
}
