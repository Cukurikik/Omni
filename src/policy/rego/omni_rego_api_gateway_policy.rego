# OMNI MOTHER — SEMESTER 14 BATCH 36
# Rego — Security & Policy Layer (OMNI Zero-Mock Implementation)
# Implements production-grade API Gateway rate limit policy.
# Absorbs patterns from: github.com/open-policy-agent/gatekeeper, Envoy ext_authz

package omni.policy.api_gateway

import rego.v1

# Default deny
default allow := false
default rate_limit_exceeded := false
default is_authenticated := false

# ============================================================================
# API Key Authentication Policy
# ============================================================================

# Valid API keys with their tier and rate limits
api_key_registry := {
    "omni-key-prod-001": {"tier": "enterprise", "rps_limit": 10000, "daily_limit": 1000000},
    "omni-key-prod-002": {"tier": "professional", "rps_limit": 1000, "daily_limit": 100000},
    "omni-key-dev-001":  {"tier": "developer", "rps_limit": 100, "daily_limit": 10000},
}

# Check if authentication is valid
is_authenticated if {
    api_key := input.request.headers["x-api-key"]
    api_key_registry[api_key]
}

# ============================================================================
# Rate Limiting Policy
# ============================================================================

# Get the client's rate limit configuration
client_config := config if {
    api_key := input.request.headers["x-api-key"]
    config := api_key_registry[api_key]
}

# Check if current request rate exceeds the per-second limit
rate_limit_exceeded if {
    client_config
    input.metrics.current_rps > client_config.rps_limit
}

# Check if daily quota is exhausted
daily_quota_exceeded if {
    client_config
    input.metrics.daily_requests > client_config.daily_limit
}

# ============================================================================
# Path-Based Access Control
# ============================================================================

# Protected paths that require specific tiers
path_tier_requirements := {
    "/api/v1/admin":     "enterprise",
    "/api/v1/analytics": "professional",
    "/api/v1/billing":   "enterprise",
    "/api/v1/deploy":    "professional",
}

# Check if the client's tier has access to the requested path
path_access_allowed if {
    not path_tier_requirements[input.request.path]
}

path_access_allowed if {
    required_tier := path_tier_requirements[input.request.path]
    client_config.tier == required_tier
}

path_access_allowed if {
    # Enterprise tier has access to everything
    client_config.tier == "enterprise"
}

# ============================================================================
# Request Size Policy
# ============================================================================

max_body_size_bytes := 10485760  # 10MB

request_too_large if {
    input.request.body_size_bytes > max_body_size_bytes
}

# ============================================================================
# IP Allowlist/Denylist
# ============================================================================

denied_ips := {"10.0.0.99", "192.168.1.200"}

ip_denied if {
    denied_ips[input.request.source_ip]
}

# ============================================================================
# Main Authorization Decision
# ============================================================================

allow if {
    is_authenticated
    not rate_limit_exceeded
    not daily_quota_exceeded
    path_access_allowed
    not request_too_large
    not ip_denied
}

# ============================================================================
# Decision Reasons (for response headers)
# ============================================================================

reasons contains "unauthenticated" if { not is_authenticated }
reasons contains "rate_limit_exceeded" if { rate_limit_exceeded }
reasons contains "daily_quota_exhausted" if { daily_quota_exceeded }
reasons contains "path_forbidden" if { not path_access_allowed }
reasons contains "request_too_large" if { request_too_large }
reasons contains "ip_denied" if { ip_denied }

# ============================================================================
# Response Headers
# ============================================================================

response_headers["X-RateLimit-Limit"] := sprintf("%d", [client_config.rps_limit]) if {
    client_config
}

response_headers["X-RateLimit-Remaining"] := sprintf("%d", [remaining]) if {
    client_config
    remaining := client_config.rps_limit - input.metrics.current_rps
    remaining >= 0
}

response_headers["X-Omni-Policy-Engine"] := "OmniAPIGatewayPolicy/1.0.0"
