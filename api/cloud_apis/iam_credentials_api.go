package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"cloud.google.com/go/iam/credentials/apiv1"
	"cloud.google.com/go/iam/credentials/apiv1/credentialspb"
	"google.golang.org/api/option"
)

// =======================================================================
// 🔐 OMNI NATIVE BRIDGE: IAM CREDENTIALS (GCP)
// =======================================================================
// Modul Golang murni berkecepatan tinggi untuk men-generate token
// Service Account secara dinamis untuk OMNI Microservices.

type IAMCredentialsBridge struct {}

// GenerateAccessToken merepresentasikan FFI gcp::InitializeIAMCredentials::GenerateAccessToken
func (i *IAMCredentialsBridge) GenerateAccessToken(targetServiceAccount string, scopes []string) (string, error) {
	log.Printf("[OMNI-NATIVE-IAM] Membangun koneksi memori IAM Credentials untuk %s", targetServiceAccount)

	ctx := context.Background()
	
	// Menggunakan Application Default Credentials (ADC) yang baru saja kita atur
	c, err := credentials.NewIamCredentialsClient(ctx, option.WithTelemetryDisabled())
	if err != nil {
		log.Printf("[ERROR] Gagal memuat Native IAM Credentials Client: %v", err)
		return "", err
	}
	defer c.Close()

	if len(scopes) == 0 {
		scopes = []string{"https://www.googleapis.com/auth/cloud-platform"}
	}

	req := &credentialspb.GenerateAccessTokenRequest{
		Name:  fmt.Sprintf("projects/-/serviceAccounts/%s", targetServiceAccount),
		Scope: scopes,
	}

	resp, err := c.GenerateAccessToken(ctx, req)
	if err != nil {
		log.Printf("[ERROR] Impersonation ditolak oleh GCP IAM: %v", err)
		return "", err
	}

	log.Printf("✅ [OMNI-NATIVE-IAM] Token berhasil di-minting. Kadaluarsa dalam: %v", resp.GetExpireTime().AsTime())
	return resp.GetAccessToken(), nil
}
