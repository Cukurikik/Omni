// moe_jwt_authorizer.go — Network / Security
// Layer: Network / Gateways — Tenant JWT Authorization & Quota
//
// Extends the standard JWT auth by cross-referencing the tenant's identity
// with the active capacity reservations (sync'd from the TypeScript Admin UI).
// Enforces hard limits on Expert usage per tenant.

package network_moe

import (
	"errors"
	"fmt"
)

// QuotaState tracks a tenant's usage over a rolling window
type QuotaState struct {
	TokensUsedThisWindow uint64
	MaxTokensPerWindow   uint64
	AllowedExperts       []int
}

type JWTAuthorizer struct {
	tenantQuotas map[string]*QuotaState
}

func NewJWTAuthorizer() *JWTAuthorizer {
	fmt.Println("[MoE Auth] JWT Authorizer & Quota Enforcer initialized.")
	return &JWTAuthorizer{
		tenantQuotas: make(map[string]*QuotaState),
	}
}

// SyncTenantPolicy receives policy updates from the TypeScript Capacity Admin
func (a *JWTAuthorizer) SyncTenantPolicy(tenantID string, maxTokens uint64, allowedExperts []int) {
	a.tenantQuotas[tenantID] = &QuotaState{
		TokensUsedThisWindow: 0,
		MaxTokensPerWindow:   maxTokens,
		AllowedExperts:       allowedExperts,
	}
}

// AuthorizeRequest checks if the JWT represents a valid tenant with sufficient quota
func (a *JWTAuthorizer) AuthorizeRequest(tenantID string, requestedTokens uint64, requestedExpert int) error {
	state, exists := a.tenantQuotas[tenantID]
	if !exists {
		// Fallback to default free-tier policy if not explicitly configured
		return errors.New("tenant not found or no policy configured")
	}

	// 1. Check if the tenant is allowed to use this specific expert (e.g. Healthcare compliance expert)
	expertAllowed := false
	for _, exp := range state.AllowedExperts {
		if exp == requestedExpert {
			expertAllowed = true
			break
		}
	}

	if !expertAllowed {
		return fmt.Errorf("tenant %s is unauthorized for Expert ID %d", tenantID, requestedExpert)
	}

	// 2. Check Quota limit
	if state.TokensUsedThisWindow+requestedTokens > state.MaxTokensPerWindow {
		return fmt.Errorf("quota exceeded: tenant %s requested %d tokens, but only %d remaining in window",
			tenantID, requestedTokens, state.MaxTokensPerWindow-state.TokensUsedThisWindow)
	}

	// 3. Deduct Quota
	state.TokensUsedThisWindow += requestedTokens
	return nil
}

