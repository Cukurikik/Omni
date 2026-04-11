package cloud_apis

import (
	"context"
	"fmt"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/remoteconfig"
	"google.golang.org/api/option"
)

// ==========================================
// 🎛️ OMNI FIREBASE REMOTE CONFIG — FEATURE FLAGS
// ==========================================
// Firebase Remote Config memungkinkan perubahan konfigurasi app
// tanpa perlu deploy ulang.
//
// OMNI Framework menggunakan Remote Config untuk:
//   - Feature flags (A/B testing, canary rollout)
//   - Dynamic pricing tiers per region
//   - Kill switch untuk fitur bermasalah
//   - Runtime configuration per tenant
//
// Target ARR: bagian dari SaaS feature management layer
// ==========================================

// RemoteConfigBridge menyediakan akses ke Firebase Remote Config Server API
type RemoteConfigBridge struct {
	projectID      string
	credentialPath string
}

// NewRemoteConfigBridge membuat bridge baru ke Remote Config
func NewRemoteConfigBridge(projectID, credentialPath string) *RemoteConfigBridge {
	return &RemoteConfigBridge{
		projectID:      projectID,
		credentialPath: credentialPath,
	}
}

// getRemoteConfigClient menginisialisasi Remote Config client
func (r *RemoteConfigBridge) getRemoteConfigClient(ctx context.Context) (*remoteconfig.Client, error) {
	var app *firebase.App
	var err error

	if r.credentialPath != "" {
		opt := option.WithCredentialsFile(r.credentialPath)
		app, err = firebase.NewApp(ctx, nil, opt)
	} else {
		app, err = firebase.NewApp(ctx, nil)
	}
	if err != nil {
		return nil, fmt.Errorf("OMNI_REMOTECONFIG_ERROR: gagal inisialisasi app: %v", err)
	}

	client, err := app.RemoteConfig(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_REMOTECONFIG_ERROR: gagal membuat client: %v", err)
	}
	return client, nil
}

// GetServerTemplate mengambil server template Remote Config terbaru
func (r *RemoteConfigBridge) GetServerTemplate(ctx context.Context, defaultConfig map[string]interface{}) (*remoteconfig.ServerTemplate, error) {
	client, err := r.getRemoteConfigClient(ctx)
	if err != nil {
		return nil, err
	}

	tmpl, err := client.GetServerTemplate(ctx, defaultConfig)
	if err != nil {
		return nil, fmt.Errorf("OMNI_REMOTECONFIG_ERROR: gagal mengambil server template: %v", err)
	}

	log.Printf("🎛️ [OMNI REMOTE CONFIG] Server template berhasil diambil")
	return tmpl, nil
}
