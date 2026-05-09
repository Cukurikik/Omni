package omni.network.authz

# OMNI MOTHER: Mutual TLS Authentication Policy

default allow_peer = false

allow_peer {
    input.cert_issuer == "omni_ca"
    input.peer_role == "expert_node"
}
