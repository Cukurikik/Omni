package cloud_apis

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/auth"
)

// ==========================================
// 🛡️ OMNI FIREBASE AUTHENTICATION WRAPPER
// ==========================================
// Mengintegrasikan Firebase Identity Toolkit untuk otentikasi Zero-Trust
// pada ekosistem OMNI.

type OmniFirebaseAuth struct {
	Client *auth.Client
}

/// Menginisialisasi OMNI Auth Node Backend 
/// @since 2.0.0
/// @tags ["firebase", "auth", "security"]
func NewOmniFirebaseAuth(ctx context.Context, app *firebase.App) (*OmniFirebaseAuth, error) {
	client, err := app.Auth(ctx)
	if err != nil {
		log.Printf("❌ [OMNI-AUTH] Gagal memuat Identity Client: %v", err)
		return nil, fmt.Errorf("auth error: %w", err)
	}
	fmt.Println("✅ [OMNI-AUTH] Modul Identity Toolkit Firebase OMNI Diaktifkan.")
	return &OmniFirebaseAuth{Client: client}, nil
}

/// Memvalidasi JWT Node Mobile Flutter atau UAST Node.js
func (o *OmniFirebaseAuth) VerifyOmniToken(ctx context.Context, idToken string) (*auth.Token, error) {
	token, err := o.Client.VerifyIDToken(ctx, idToken)
	if err != nil {
		return nil, fmt.Errorf("jwt validation failed: %w", err)
	}
	return token, nil
}
