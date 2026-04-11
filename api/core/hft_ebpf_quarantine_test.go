package core

import (
	"strings"
	"testing"
)

func TestHFTQuarantine(t *testing.T) {
	// Test Case 1: Free Tier mencoba menggunakan modul eBPF
	errFree := ValidatePackagePermissions("omni-hft-modules", []string{"allow_ebpf"}, TierFree)
	if errFree == nil {
		t.Fatalf("Expected an error for Free Tier accessing eBPF, got nil")
	}
	if !strings.Contains(errFree.Error(), "QUARANTINE_LOCKED") {
		t.Errorf("Expected QUARANTINE_LOCKED error, got: %v", errFree)
	}

	// Test Case 2: Premium Tier mencoba menggunakan modul eBPF (Batas HFT adalah Enterprise)
	errPremium := ValidatePackagePermissions("omni-hft-modules", []string{"allow_ebpf"}, TierPremium)
	if errPremium == nil {
		t.Fatalf("Expected an error for Premium Tier accessing eBPF (HFT requires Enterprise), got nil")
	}
	if !strings.Contains(errPremium.Error(), "QUARANTINE_LOCKED") {
		t.Errorf("Expected QUARANTINE_LOCKED error, got: %v", errPremium)
	}

	// Test Case 3: Enterprise Tier (Harus Lolos)
	errEnterprise := ValidatePackagePermissions("omni-hft-modules", []string{"allow_ebpf", "allow_realtime"}, TierEnterprise)
	if errEnterprise != nil {
		t.Errorf("Expected Enterprise Tier to pass quarantine for HFT, but got error: %v", errEnterprise)
	}

	t.Log("✅ OMNI HFT eBPF & Realtime Quarantine tests passed!")
}
