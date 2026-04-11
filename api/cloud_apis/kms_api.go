package cloud_apis

import (
	"context"
	"fmt"
	"log"

	kms "cloud.google.com/go/kms/apiv1"
	"cloud.google.com/go/kms/apiv1/kmspb"
)

// ==========================================
// 🔐 OMNI CLOUD KMS — ENTERPRISE KEY MANAGEMENT
// ==========================================
// Cloud KMS menyediakan manajemen kunci kriptografi tersentralisasi.
//
// OMNI Framework menggunakan KMS untuk:
//   - Enkripsi data at rest (database fields, PII)
//   - Enkripsi data in transit (payloads, tokens)
//   - Envelope encryption untuk OMNI Enterprise
// ==========================================

// KMSBridge menyediakan akses native ke Cloud KMS
type KMSBridge struct {
	projectID string
	location  string
	keyRing   string
	cryptoKey string
}

// NewKMSBridge membuat bridge baru ke Cloud KMS
func NewKMSBridge(projectID, location, keyRing, cryptoKey string) *KMSBridge {
	return &KMSBridge{
		projectID: projectID,
		location:  location,
		keyRing:   keyRing,
		cryptoKey: cryptoKey,
	}
}

// keyPath menghasilkan fully-qualified key path
func (k *KMSBridge) keyPath() string {
	return fmt.Sprintf("projects/%s/locations/%s/keyRings/%s/cryptoKeys/%s",
		k.projectID, k.location, k.keyRing, k.cryptoKey)
}

// Encrypt mengenkripsi plaintext menggunakan algoritma simetris Cloud KMS
func (k *KMSBridge) Encrypt(ctx context.Context, plaintext []byte) ([]byte, error) {
	client, err := kms.NewKeyManagementClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_KMS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &kmspb.EncryptRequest{
		Name:      k.keyPath(),
		Plaintext: plaintext,
	}

	resp, err := client.Encrypt(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_KMS_ERROR: gagal mengenkripsi data: %v", err)
	}

	log.Printf("🔐 [OMNI KMS] Data berhasil dienkripsi (%d bytes)", len(resp.Ciphertext))
	return resp.Ciphertext, nil
}

// Decrypt mendekripsi ciphertext yang sebelumnya dienkripsi dengan Cloud KMS
func (k *KMSBridge) Decrypt(ctx context.Context, ciphertext []byte) ([]byte, error) {
	client, err := kms.NewKeyManagementClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_KMS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &kmspb.DecryptRequest{
		Name:       k.keyPath(),
		Ciphertext: ciphertext,
	}

	resp, err := client.Decrypt(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_KMS_ERROR: gagal mendekripsi data: %v", err)
	}

	log.Printf("🔐 [OMNI KMS] Data berhasil didekripsi (%d bytes)", len(resp.Plaintext))
	return resp.Plaintext, nil
}
