# OMNI Framework - OPA Rego Policy
# Dynamically restricts expert execution based on payload sensitivity and user roles

package omni.security.moe

default allow_execution = false

# Rules for evaluating if an incoming request can hit specific experts
allow_execution {
    input.request.expert_type == "general"
    input.user.status == "active"
}

allow_execution {
    input.request.expert_type == "financial_analysis"
    input.user.role == "analyst"
    input.request.encryption == "TLS1.3"
}

allow_execution {
    input.request.expert_type == "medical_diagnosis"
    input.user.role == "doctor"
    input.user.mfa_verified == true
}

deny_execution[msg] {
    input.request.expert_type == "medical_diagnosis"
    not input.user.mfa_verified
    msg := "Medical expert routing requires MFA verification"
}

deny_execution[msg] {
    input.request.payload_size_mb > 10
    input.user.tier != "enterprise"
    msg := "Payloads > 10MB require Enterprise tier for MoE processing"
}
