package omni.moe.authz

# OMNI MOTHER Production Zero-Mock OPA Policy
# Open Policy Agent (Rego) file dictating fine-grained access control
# for MoE experts based on JWT roles and usage quotas.

default allow = false

# Allow if user is admin
allow {
    input.user.role == "admin"
}

# Allow if user has access to the specific domain expert
allow {
    input.user.role == "developer"
    allowed_expert_domain
    quota_not_exceeded
}

allowed_expert_domain {
    # Check if the requested expert domain is in the user's allowed list
    expert := input.request.expert_domain
    expert == input.user.allowed_domains[_]
}

quota_not_exceeded {
    input.request.estimated_tokens < input.user.remaining_quota
}

# Deny highly sensitive experts to standard users
deny[msg] {
    input.request.expert_domain == "financial_pii"
    input.user.role != "admin"
    msg := "OMNI SECURE: Access to financial_pii expert is restricted to admins."
}
