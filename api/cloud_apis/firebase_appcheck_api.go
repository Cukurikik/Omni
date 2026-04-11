package cloud_apis

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/appcheck"
	"google.golang.org/api/option"
)

// ==========================================
// 🛡️ OMNI FIREBASE APP CHECK — REQUEST VERIFICATION
// ==========================================
// Firebase App Check melindungi backend dari request tidak sah.
//
// OMNI Framework menggunakan App Check untuk:
//   - Memvalidasi bahwa request hanya datang dari app resmi
//   - Mencegah abuse dan scraping pada API endpoint
//   - Layer keamanan tambahan di atas Firebase Auth
//
// Target ARR: bagian dari Enterprise Security tier
// ==========================================

// AppCheckBridge menyediakan akses ke Firebase App Check
type AppCheckBridge struct {
	projectID      string
	credentialPath string
}

// NewAppCheckBridge membuat bridge baru ke Firebase App Check
func NewAppCheckBridge(projectID, credentialPath string) *AppCheckBridge {
	return &AppCheckBridge{
		projectID:      projectID,
		credentialPath: credentialPath,
	}
}

// getAppCheckClient menginisialisasi Firebase App dan mengembalikan AppCheck client
func (a *AppCheckBridge) getAppCheckClient(ctx context.Context) (*appcheck.Client, error) {
	var app *firebase.App
	var err error

	if a.credentialPath != "" {
		opt := option.WithCredentialsFile(a.credentialPath)
		app, err = firebase.NewApp(ctx, nil, opt)
	} else {
		app, err = firebase.NewApp(ctx, nil)
	}
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPCHECK_ERROR: gagal inisialisasi app: %v", err)
	}

	client, err := app.AppCheck(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPCHECK_ERROR: gagal membuat client: %v", err)
	}
	return client, nil
}

// VerifyToken memverifikasi App Check token dari client app
func (a *AppCheckBridge) VerifyToken(ctx context.Context, token string) (*appcheck.DecodedAppCheckToken, error) {
	client, err := a.getAppCheckClient(ctx)
	if err != nil {
		return nil, err
	}

	decoded, err := client.VerifyToken(token)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPCHECK_ERROR: token tidak valid: %v", err)
	}

	log.Printf("🛡️ [OMNI APP CHECK] Token valid — AppID: %s, Issuer: %s",
		decoded.AppID, decoded.Issuer)
	return decoded, nil
}
