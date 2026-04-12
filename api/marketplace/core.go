package marketplace

import (
	"fmt"
	"sync"
)

// ==========================================
// 🛒 OMNI NEXUS MARKETPLACE (Phase 27)
// ==========================================
// Mengakomodasi Blueprint Section 5.4 
// (Target $50.000/Tahun via 250 instalasi Premium Packages).

type Package struct {
	ID    string
	Name  string
	Tier  string
	Price float64
}

type OmniMarket struct {
	mu       sync.RWMutex
	Packages map[string]*Package
	Revenue  float64
}

func InitializeMarket() *OmniMarket {
	market := &OmniMarket{
		Packages: make(map[string]*Package),
		Revenue:  0,
	}

	// Seed Premium Packages
	market.Packages["omni-global-tax-engine"] = &Package{"pkg-001", "omni-global-tax-engine", "premium", 299}
	market.Packages["omni-kyc-identity-suite"] = &Package{"pkg-002", "omni-kyc-identity-suite", "premium", 499}
	market.Packages["omni-ai-video-compressor"] = &Package{"pkg-003", "omni-ai-video-compressor", "premium", 199}

	return market
}

func (m *OmniMarket) BuyPackage(id string) (string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	pkg, exists := m.Packages[id]
	if !exists {
		return "", fmt.Errorf("Package %s tidak ada dalam OMNI Nexus", id)
	}

	m.Revenue += pkg.Price
	return fmt.Sprintf("✅ Instalasi sukses: %s. Total Pendapatan Nexus: $%.2f", pkg.Name, m.Revenue), nil
}
