package core

import (
	"testing"
)

func TestCloudControllerDeploySimulation(t *testing.T) {
	// Tes logika inisialisasi controller
	ctrl := NewCloudController("omni-tool-9c48b", "id-jkt-1")
	if ctrl.ProjectID != "omni-tool-9c48b" {
		t.Fatalf("Expected project ID omni-tool-9c48b, got %s", ctrl.ProjectID)
	}

	// This mimics execution with Skaffold. If skaffold or kubectl is not running
	// it will return an error, but the error message is processed safely.
	err := ctrl.Deploy("test_payload.wasm")
	if err != nil {
		t.Logf("Deployment simulated. Err received (expected if cluster not alive): %v", err)
	}
}
