package cloud_apis

import (
	"context"
	"fmt"
	"log"
	"sync"

	secretmanager "cloud.google.com/go/secretmanager/apiv1"
	"cloud.google.com/go/secretmanager/apiv1/secretmanagerpb"
)

// ==========================================
// 🔐 OMNI SECRET MANAGER — ENTERPRISE VAULT
// ==========================================
// Menggantikan file .env berbahaya dengan Google Cloud
// Secret Manager yang terenkripsi AES-256-GCM oleh Google KMS.
//
// Secrets yang tersimpan:
//   - omni-gemini-api-key     → Gemini API Key
//   - omni-database-url       → PostgreSQL Connection String
//   - connection-*-github-*   → GitHub OAuth Token
//
// Tidak ada rahasia yang boleh disimpan di file teks mentah!
// ==========================================

// SecretVault adalah wrapper aman untuk Google Secret Manager
type SecretVault struct {
	client    *secretmanager.Client
	projectID string
	cache     map[string]string
	mu        sync.RWMutex
}

// VaultError implementasi monadic error (OMNI Strict Rule 3.1)
type VaultError struct {
	SecretName string
	Message    string
	Code       string
}

func (e *VaultError) Error() string {
	return fmt.Sprintf("OMNI_VAULT_ERROR [%s] secret=%s: %s", e.Code, e.SecretName, e.Message)
}

const (
	ErrVaultInit      = "E_VAULT_001"
	ErrSecretNotFound = "E_VAULT_002"
	ErrAccessDenied   = "E_VAULT_003"
	ErrSecretCreate   = "E_VAULT_004"
)

// Well-known OMNI secret names
const (
	SecretGeminiAPIKey = "omni-gemini-api-key"
	SecretDatabaseURL  = "omni-database-url"
)

// NewSecretVault membuat koneksi baru ke Google Secret Manager
func NewSecretVault(ctx context.Context, projectID string) (*SecretVault, error) {
	client, err := secretmanager.NewClient(ctx)
	if err != nil {
		return nil, &VaultError{
			SecretName: "*",
			Message:    fmt.Sprintf("Gagal menginisialisasi Secret Manager client: %v", err),
			Code:       ErrVaultInit,
		}
	}

	log.Printf("🔐 [OMNI VAULT] Secret Manager terhubung ke project: %s", projectID)
	return &SecretVault{
		client:    client,
		projectID: projectID,
		cache:     make(map[string]string),
	}, nil
}

// GetSecret mengambil nilai secret terbaru dari vault Google
// Menggunakan cache untuk menghindari panggilan berulang ke GCP
func (v *SecretVault) GetSecret(ctx context.Context, secretName string) (string, error) {
	// Cek cache dulu
	v.mu.RLock()
	if cached, ok := v.cache[secretName]; ok {
		v.mu.RUnlock()
		return cached, nil
	}
	v.mu.RUnlock()

	// Baca dari GCP Secret Manager
	resourceName := fmt.Sprintf("projects/%s/secrets/%s/versions/latest", v.projectID, secretName)
	result, err := v.client.AccessSecretVersion(ctx, &secretmanagerpb.AccessSecretVersionRequest{
		Name: resourceName,
	})
	if err != nil {
		return "", &VaultError{
			SecretName: secretName,
			Message:    fmt.Sprintf("Gagal mengakses secret: %v", err),
			Code:       ErrSecretNotFound,
		}
	}

	value := string(result.Payload.Data)

	// Cache hasil
	v.mu.Lock()
	v.cache[secretName] = value
	v.mu.Unlock()

	log.Printf("🔐 [OMNI VAULT] Secret '%s' berhasil dimuat dari GCP", secretName)
	return value, nil
}

// GetGeminiAPIKey shortcut untuk mengambil Gemini API Key
func (v *SecretVault) GetGeminiAPIKey(ctx context.Context) (string, error) {
	return v.GetSecret(ctx, SecretGeminiAPIKey)
}

// GetDatabaseURL shortcut untuk mengambil Database Connection String
func (v *SecretVault) GetDatabaseURL(ctx context.Context) (string, error) {
	return v.GetSecret(ctx, SecretDatabaseURL)
}

// CreateSecret membuat secret baru di vault GCP
func (v *SecretVault) CreateSecret(ctx context.Context, secretName string, value string) error {
	// 1. Buat secret container
	createReq := &secretmanagerpb.CreateSecretRequest{
		Parent:   fmt.Sprintf("projects/%s", v.projectID),
		SecretId: secretName,
		Secret: &secretmanagerpb.Secret{
			Replication: &secretmanagerpb.Replication{
				Replication: &secretmanagerpb.Replication_Automatic_{
					Automatic: &secretmanagerpb.Replication_Automatic{},
				},
			},
		},
	}

	secret, err := v.client.CreateSecret(ctx, createReq)
	if err != nil {
		return &VaultError{
			SecretName: secretName,
			Message:    fmt.Sprintf("Gagal membuat secret container: %v", err),
			Code:       ErrSecretCreate,
		}
	}

	// 2. Tambahkan version dengan nilai
	addReq := &secretmanagerpb.AddSecretVersionRequest{
		Parent: secret.Name,
		Payload: &secretmanagerpb.SecretPayload{
			Data: []byte(value),
		},
	}

	_, err = v.client.AddSecretVersion(ctx, addReq)
	if err != nil {
		return &VaultError{
			SecretName: secretName,
			Message:    fmt.Sprintf("Gagal menambahkan secret version: %v", err),
			Code:       ErrSecretCreate,
		}
	}

	log.Printf("🔐 [OMNI VAULT] Secret '%s' berhasil dibuat dan tersimpan!", secretName)
	return nil
}

// ListSecrets menampilkan semua secret yang ada di project
func (v *SecretVault) ListSecrets(ctx context.Context) ([]string, error) {
	req := &secretmanagerpb.ListSecretsRequest{
		Parent: fmt.Sprintf("projects/%s", v.projectID),
	}

	var names []string
	it := v.client.ListSecrets(ctx, req)
	for {
		secret, err := it.Next()
		if err != nil {
			break
		}
		names = append(names, secret.Name)
	}

	log.Printf("🔐 [OMNI VAULT] Ditemukan %d secrets di project %s", len(names), v.projectID)
	return names, nil
}

// InvalidateCache menghapus cache lokal (force reload dari GCP)
func (v *SecretVault) InvalidateCache() {
	v.mu.Lock()
	v.cache = make(map[string]string)
	v.mu.Unlock()
	log.Println("🔐 [OMNI VAULT] Cache di-invalidasi — secrets akan dimuat ulang dari GCP")
}

// Close menutup koneksi ke Secret Manager
func (v *SecretVault) Close() error {
	if v.client != nil {
		return v.client.Close()
	}
	return nil
}
