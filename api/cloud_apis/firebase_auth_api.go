package cloud_apis

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/auth"
	"google.golang.org/api/option"
)

// ==========================================
// 🔑 OMNI FIREBASE AUTH — IDENTITY & ACCESS
// ==========================================
// Firebase Auth menyediakan identity platform untuk autentikasi pengguna.
//
// OMNI Framework menggunakan Firebase Auth untuk:
//   - Email/password, Google, GitHub sign-in
//   - Custom Claims untuk RBAC (Role-Based Access Control)
//   - Token verification untuk API Gateway
//   - Multi-tenancy isolation per OMNI Cloud tenant
//
// Target ARR: bagian dari Enterprise SaaS auth layer
// ==========================================

// FirebaseAuthBridge menyediakan akses native ke Firebase Authentication
type FirebaseAuthBridge struct {
	projectID      string
	credentialPath string
}

// NewFirebaseAuthBridge membuat bridge baru ke Firebase Auth
func NewFirebaseAuthBridge(projectID, credentialPath string) *FirebaseAuthBridge {
	return &FirebaseAuthBridge{
		projectID:      projectID,
		credentialPath: credentialPath,
	}
}

// getAuthClient menginisialisasi Firebase App dan mengembalikan Auth client
func (f *FirebaseAuthBridge) getAuthClient(ctx context.Context) (*auth.Client, error) {
	var app *firebase.App
	var err error

	if f.credentialPath != "" {
		opt := option.WithCredentialsFile(f.credentialPath)
		app, err = firebase.NewApp(ctx, nil, opt)
	} else {
		// Gunakan Application Default Credentials (ADC)
		app, err = firebase.NewApp(ctx, nil)
	}
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: gagal inisialisasi app: %v", err)
	}

	client, err := app.Auth(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: gagal membuat auth client: %v", err)
	}
	return client, nil
}

// CreateUser membuat akun pengguna baru di Firebase Auth
func (f *FirebaseAuthBridge) CreateUser(ctx context.Context, email, password, displayName string) (*auth.UserRecord, error) {
	client, err := f.getAuthClient(ctx)
	if err != nil {
		return nil, err
	}

	params := (&auth.UserToCreate{}).
		Email(email).
		Password(password).
		DisplayName(displayName).
		EmailVerified(false)

	user, err := client.CreateUser(ctx, params)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: gagal membuat user: %v", err)
	}

	log.Printf("🔑 [OMNI AUTH] User berhasil dibuat: %s (UID: %s)", email, user.UID)
	return user, nil
}

// GetUser mengambil data user berdasarkan UID
func (f *FirebaseAuthBridge) GetUser(ctx context.Context, uid string) (*auth.UserRecord, error) {
	client, err := f.getAuthClient(ctx)
	if err != nil {
		return nil, err
	}

	user, err := client.GetUser(ctx, uid)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: gagal mengambil user %s: %v", uid, err)
	}

	log.Printf("🔑 [OMNI AUTH] User ditemukan: %s (%s)", user.DisplayName, user.Email)
	return user, nil
}

// VerifyIDToken memverifikasi JWT token dari client-side Firebase SDK
func (f *FirebaseAuthBridge) VerifyIDToken(ctx context.Context, idToken string) (*auth.Token, error) {
	client, err := f.getAuthClient(ctx)
	if err != nil {
		return nil, err
	}

	token, err := client.VerifyIDToken(ctx, idToken)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: token tidak valid: %v", err)
	}

	log.Printf("🔑 [OMNI AUTH] Token valid untuk UID: %s", token.UID)
	return token, nil
}

// SetCustomClaims menetapkan custom claims (RBAC roles) pada user
func (f *FirebaseAuthBridge) SetCustomClaims(ctx context.Context, uid string, claims map[string]interface{}) error {
	client, err := f.getAuthClient(ctx)
	if err != nil {
		return err
	}

	err = client.SetCustomUserClaims(ctx, uid, claims)
	if err != nil {
		return fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: gagal set custom claims untuk %s: %v", uid, err)
	}

	log.Printf("🔑 [OMNI AUTH] Custom claims berhasil di-set untuk UID: %s", uid)
	return nil
}

// DeleteUser menghapus user berdasarkan UID
func (f *FirebaseAuthBridge) DeleteUser(ctx context.Context, uid string) error {
	client, err := f.getAuthClient(ctx)
	if err != nil {
		return err
	}

	err = client.DeleteUser(ctx, uid)
	if err != nil {
		return fmt.Errorf("OMNI_FIREBASE_AUTH_ERROR: gagal menghapus user %s: %v", uid, err)
	}

	log.Printf("🔑 [OMNI AUTH] User berhasil dihapus: %s", uid)
	return nil
}

// ListUsers mengembalikan daftar pengguna dengan pagination
func (f *FirebaseAuthBridge) ListUsers(ctx context.Context, maxResults int) ([]*auth.ExportedUserRecord, error) {
	client, err := f.getAuthClient(ctx)
	if err != nil {
		return nil, err
	}

	iter := client.Users(ctx, "")
	var users []*auth.ExportedUserRecord
	count := 0

	for {
		user, err := iter.Next()
		if err != nil {
			break
		}
		users = append(users, user)
		count++
		if count >= maxResults {
			break
		}
	}

	log.Printf("🔑 [OMNI AUTH] Listed %d users", len(users))
	return users, nil
}
