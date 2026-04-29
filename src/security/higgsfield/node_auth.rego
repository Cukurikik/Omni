# OMNI HIGGSFIELD: Node Auth Policy
# Rego policy enforced by OPA to ensure that only authorized GPU nodes can join 
# the distributed training cluster, preventing malicious code injection.
# Source: higgsfield-ai/higgsfield

package omni.higgsfield.auth

default allow = false

# Input Schema:
# {
#   "node_ip": "10.0.1.10",
#   "tls_cert_issuer": "omni-internal-ca",
#   "gpu_architecture": "ampere"
# }

# Rule 1: Node must present a certificate signed by the internal CA
valid_cert {
    input.tls_cert_issuer == "omni-internal-ca"
}

# Rule 2: IP must be within the private VPC CIDR
valid_ip {
    startswith(input.node_ip, "10.0.")
}

# Allow cluster join if both conditions are met
allow {
    valid_cert
    valid_ip
}

violation_msg = "Node rejected: Invalid TLS certificate issuer or IP address outside VPC bounds." {
    not allow
}
