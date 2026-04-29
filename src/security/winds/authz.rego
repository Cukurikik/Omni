// OMNI FRAMEWORK: BATCH 38
// ENGINE: WINDS SECURITY POLICY (REGO)
// DOMAIN: SECURITY / POLICY
// ZERO MOCK - PRODUCTION READY
// ==========================================

package omni.winds.authz

default allow = false

# Allow access if the user has an active premium subscription
allow {
    input.user.subscription_status == "active"
    input.request.action == "read_podcast"
}

# Allow admins to bypass
allow {
    input.user.roles[_] == "admin"
}

# Rate limiting rules
deny[msg] {
    input.user.request_count > 1000
    msg := "RATE_LIMIT_EXCEEDED"
}

# Explicitly deny banned users
deny[msg] {
    input.user.status == "banned"
    msg := "USER_BANNED"
}
