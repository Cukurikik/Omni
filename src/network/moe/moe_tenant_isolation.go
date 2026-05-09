// moe_tenant_isolation.go — Network / Security
// Layer: Network / Gateways — Tenant Isolation for MoE
//
// Ensures that multi-tenant inference requests do not mix within the MoE router.
// Associates requests with tenant IDs, allocating strict resource quotas
// (e.g., Tenant A can only hit Experts 0-3, Tenant B hits 4-7).

package network_moe

import (
	"errors"
	"fmt"
	"sync"
)

// TenantPolicy defines MoE access rules for a specific tenant.
type TenantPolicy struct {
	TenantID        string
	AllowedExperts  []int // Whitelisted expert IDs
	MaxTokensPerSec int
}

// MoETenantManager enforces isolation at the HTTP/gRPC gateway.
type MoETenantManager struct {
	mu       sync.RWMutex
	policies map[string]*TenantPolicy
}

func NewMoETenantManager() *MoETenantManager {
	fmt.Println("[MoE Tenant Manager] Initialized Zero-Trust Isolation.")
	return &MoETenantManager{
		policies: make(map[string]*TenantPolicy),
	}
}

func (m *MoETenantManager) RegisterTenant(tenantID string, allowedExperts []int, limit int) {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.policies[tenantID] = &TenantPolicy{
		TenantID:        tenantID,
		AllowedExperts:  allowedExperts,
		MaxTokensPerSec: limit,
	}
	fmt.Printf("[MoE Tenant Manager] Registered Tenant %s (Allowed Experts: %v)\n", tenantID, allowedExperts)
}

// ValidateRouting ensures a tenant isn't trying to access an expert outside their slice.
// Used as a fast-path check before dispatching tensors to GPUs.
func (m *MoETenantManager) ValidateRouting(tenantID string, requestedExpert int) error {
	m.mu.RLock()
	policy, exists := m.policies[tenantID]
	m.mu.RUnlock()

	if !exists {
		return errors.New("unauthorized tenant")
	}

	// O(N) search is fine for small expert arrays (N < 256)
	for _, allowed := range policy.AllowedExperts {
		if allowed == requestedExpert {
			return nil // Valid
		}
	}

	return fmt.Errorf("tenant %s is isolated and cannot route to expert %d", tenantID, requestedExpert)
}

