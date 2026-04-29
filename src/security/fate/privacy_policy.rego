package omni.security.fate

default allow_parameter_sync = false

# Allow parameter exchange only if DP epsilon is strictly enforced
allow_parameter_sync {
    input.contract.status == "verified"
    input.differential_privacy.epsilon <= 1.0
    input.differential_privacy.delta < 0.00001
    input.transmission.is_encrypted == true
}

deny_leak {
    input.transmission.protocol != "TLS1.3"
}
