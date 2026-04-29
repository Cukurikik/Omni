package omni.security.privategpt

# OMNI PRIVATEGPT: Data Exfiltration Prevention Policy
# Ensures that RAG agents cannot send data to unauthorized external endpoints.
# Source: imartinez/privateGPT

default allow_egress = false

# Allow egress ONLY to internal vector databases and strictly whitelisted logging servers
allow_egress {
    input.action == "network_egress"
    is_whitelisted_destination(input.destination_ip)
}

# The explicit whitelist of safe internal IP ranges (Airgapped VPCs)
is_whitelisted_destination(ip) {
    # Allow 10.x.x.x internal network
    startswith(ip, "10.")
}

is_whitelisted_destination(ip) {
    # Allow local loopback
    startswith(ip, "127.")
}

# Strictly DENY requests containing specific PII patterns in the payload payload going anywhere
deny[msg] {
    input.action == "network_egress"
    contains_sensitive_data(input.payload)
    msg := "Egress blocked: Payload contains detected PII/Sensitive data."
}

# Extremely simple mock of regex matching for SSN/Credit Cards
contains_sensitive_data(payload) {
    contains(payload, "SSN:")
}
contains_sensitive_data(payload) {
    contains(payload, "CREDIT_CARD:")
}
