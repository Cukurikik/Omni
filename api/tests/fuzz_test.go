package tests

import (
	"context"
	"testing"
	"omnitools/telepathy"
)

// ==========================================
// 🛡️ OMNI FUZZ TESTING (Phase 24)
// ==========================================
// Menjalankan native Go Fuzzing pada Telepathy Router untuk
// memastikan memori kernel C++ & Go tetap aman dari intervensi alien.

func FuzzTelepathyGatewayRouting(f *testing.F) {
	// Korpus input dasar
	f.Add("omni::Singularity::GetDiagnostics", `{"test": 123}`)
	f.Add("gcp::CloudPaaSBridge::DeployApp", `{"appName": "virus", "dockerImage": "evil:latest"}`)
	f.Add("", `{"type": "malformed"}`)
	
	f.Fuzz(func(t *testing.T, method string, payloadStr string) {
		req := telepathy.OmniRequest{
			Method: method,
			Args:   map[string]interface{}{"payload": payloadStr, "ast_buffer": payloadStr},
		}

		ctx := context.Background()

		// OMNI Router tidak boleh PANIC meskipun payloadnya berupa racun data
		defer func() {
			if r := recover(); r != nil {
				t.Errorf("🚨 [CRITICAL] Telepathy Router Kena Panic: %v dengan input: %s", r, payloadStr)
			}
		}()

		// Invoke Langsung
		res := telepathy.TelepathyRouter(ctx, req)
		
		// Validasi bahwa status hanyalah Err atau Ok
		if res.Status != "Ok" && res.Status != "Err" {
			t.Errorf("Status balasan cacat: %s", res.Status)
		}
	})
}
