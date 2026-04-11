package core

import (
	"testing"
	"strings"
)

func TestLegacyBridgeQuarantine(t *testing.T) {
	// Test Case 1: Free Tier dengan OMNI Legacy Bridge
	err := ValidatePackagePermissions("omni-legacy-bridge", []string{"allow_sidecar:jvm-11"}, TierFree)
	if err == nil {
		t.Fatalf("Expected an error for Free Tier accessing JNI, got nil")
	}
	if !strings.Contains(err.Error(), "QUARANTINE_LOCKED") {
		t.Errorf("Expected QUARANTINE_LOCKED error, got: %v", err)
	}

	// Test Case 2: Premium Tier (Harus lolos)
	errPremium := ValidatePackagePermissions("omni-legacy-bridge", []string{"allow_sidecar:dotnet-6"}, TierPremium)
	if errPremium != nil {
		t.Errorf("Expected Premium Tier to pass quarantine, but got error: %v", errPremium)
	}

	// Test Case 3: OMNI Community Module biasa (Bukan sidecar JVM/CLR)
	errNormal := ValidatePackagePermissions("omni-math", []string{"allow_thread"}, TierFree)
	if errNormal != nil {
		t.Errorf("Expected Free user to pass normal module quarantine, but got error: %v", errNormal)
	}

	t.Log("✅ OMNI Legacy Bridge Quarantine tests passed!")
}
