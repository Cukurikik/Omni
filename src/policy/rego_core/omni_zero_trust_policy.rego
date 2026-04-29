# OmniZeroTrustPolicy - OMNI Security Layer
#
# Rego (Open Policy Agent) rules mapping exact boundary enforcements
# for cross-layer communication within the OMNI execution framework.

package omni.security.zerotrust

default allow = false

# Allow UI layer to read Compute layer if token is verified
allow {
    input.source_layer == "UI"
    input.target_layer == "COMPUTE"
    input.action == "read"
    is_token_verified
}

# Never allow UI to directly access System/Memory layer
deny {
    input.source_layer == "UI"
    input.target_layer == "SYSTEM"
}

# System layer can talk to Concurrency (Network) layer if local
allow {
    input.source_layer == "SYSTEM"
    input.target_layer == "NETWORK"
    input.environment == "local_node"
}

# Monadic Error validation - requests must specify fallback intent
allow {
    input.has_monadic_fallback == true
    input.auth.role == "verified_service"
}

# Helper rule to verify tokens
is_token_verified {
    input.auth.token != ""
    # In production, check JWT signature via builtin
    # io.jwt.verify_rs256(input.auth.token, data.certificates)
    input.auth.valid == true
}
