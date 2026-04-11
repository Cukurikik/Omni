package cloud_apis

import (
	"context"
	"fmt"
	"log"

	policytroubleshooter "cloud.google.com/go/policytroubleshooter/apiv1"
	"cloud.google.com/go/policytroubleshooter/apiv1/policytroubleshooterpb"
	"google.golang.org/api/option"
)

// =======================================================================
// 🛡️ OMNI NATIVE BRIDGE: POLICY TROUBLESHOOTER (GCP)
// =======================================================================
// Modul Golang untuk mengaudit hak akses agen AI (Zero-Trust) sebelum
// mereka menyentuh database production.

type PolicyTroubleshooterBridge struct{}

// SimulateAccess merepresentasikan FFI gcp::InitializePolicyTroubleshooter::SimulateAccess
func (p *PolicyTroubleshooterBridge) SimulateAccess(principalEmail string, permission string, resource string) (bool, error) {
	log.Printf("[OMNI-NATIVE-POLICY] Memeriksa Otorisasi: %s -> %s on %s", principalEmail, permission, resource)

	ctx := context.Background()
	c, err := policytroubleshooter.NewIamCheckerClient(ctx, option.WithTelemetryDisabled())
	if err != nil {
		return false, fmt.Errorf("[ERROR] Gagal memuat Native Policy Troubleshooter: %v", err)
	}
	defer c.Close()

	req := &policytroubleshooterpb.TroubleshootIamPolicyRequest{
		AccessTuple: &policytroubleshooterpb.AccessTuple{
			Principal:        "user:" + principalEmail,
			Permission:       permission,
			FullResourceName: resource,
		},
	}

	resp, err := c.TroubleshootIamPolicy(ctx, req)
	if err != nil {
		return false, fmt.Errorf("[ERROR] Simulasi Kebijakan IAM Gagal: %v", err)
	}

	if resp.GetAccess() == policytroubleshooterpb.AccessState_GRANTED {
		log.Printf("✅ [OMNI-NATIVE-POLICY] Validasi Sukses: GRANTED")
		return true, nil
	}

	log.Printf("❌ [OMNI-NATIVE-POLICY] Validasi Ditolak: DENIED")
	return false, nil
}
