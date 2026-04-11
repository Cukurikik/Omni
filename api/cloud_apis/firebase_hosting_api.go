package cloud_apis

import (
	"context"
	"fmt"
	"log"
	"os/exec"
	"strings"
)

// ==========================================
// 🌐 OMNI FIREBASE HOSTING — STATIC & DYNAMIC WEB
// ==========================================
// Firebase Hosting menyediakan CDN global untuk web content.
//
// OMNI Framework menggunakan Firebase Hosting untuk:
//   - Hosting OMNI Dashboard (TypeScript SPA)
//   - Landing page untuk setiap OMNI Cloud tenant
//   - Preview channels untuk CI/CD staging
//
// Target ARR: bagian dari PaaS Cloud Hosting tier
// ==========================================

// FirebaseHostingBridge menyediakan akses ke Firebase Hosting via CLI
type FirebaseHostingBridge struct {
	projectID string
	siteID    string
}

// NewFirebaseHostingBridge membuat bridge baru ke Firebase Hosting
func NewFirebaseHostingBridge(projectID, siteID string) *FirebaseHostingBridge {
	return &FirebaseHostingBridge{
		projectID: projectID,
		siteID:    siteID,
	}
}

// Deploy menjalankan firebase deploy untuk hosting ke production channel
func (h *FirebaseHostingBridge) Deploy(ctx context.Context, publicDir string) (string, error) {
	args := []string{
		"deploy", "--only", "hosting",
		"--project", h.projectID,
	}

	cmd := exec.CommandContext(ctx, "firebase", args...)
	cmd.Dir = publicDir

	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("OMNI_HOSTING_ERROR: deploy gagal: %v\nOutput: %s", err, string(output))
	}

	result := string(output)
	log.Printf("🌐 [OMNI HOSTING] Deploy selesai ke project '%s'", h.projectID)
	return result, nil
}

// DeployPreview menjalankan deploy ke preview channel untuk staging/testing
func (h *FirebaseHostingBridge) DeployPreview(ctx context.Context, publicDir, channelID string) (string, error) {
	args := []string{
		"hosting:channel:deploy", channelID,
		"--project", h.projectID,
	}

	cmd := exec.CommandContext(ctx, "firebase", args...)
	cmd.Dir = publicDir

	output, err := cmd.CombinedOutput()
	if err != nil {
		return "", fmt.Errorf("OMNI_HOSTING_ERROR: preview deploy gagal: %v\nOutput: %s", err, string(output))
	}

	result := string(output)
	log.Printf("🌐 [OMNI HOSTING] Preview channel '%s' deployed", channelID)
	return result, nil
}

// ListChannels menampilkan daftar preview channels yang aktif
func (h *FirebaseHostingBridge) ListChannels(ctx context.Context) ([]string, error) {
	args := []string{
		"hosting:channel:list",
		"--project", h.projectID,
		"--json",
	}

	cmd := exec.CommandContext(ctx, "firebase", args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("OMNI_HOSTING_ERROR: gagal list channels: %v", err)
	}

	// Parse output (simplified — in production, parse JSON)
	lines := strings.Split(string(output), "\n")
	log.Printf("🌐 [OMNI HOSTING] Ditemukan %d output lines untuk channels", len(lines))
	return lines, nil
}

// GetSiteURL mengembalikan URL hosting default untuk site
func (h *FirebaseHostingBridge) GetSiteURL() string {
	if h.siteID != "" {
		return fmt.Sprintf("https://%s.web.app", h.siteID)
	}
	return fmt.Sprintf("https://%s.web.app", h.projectID)
}
