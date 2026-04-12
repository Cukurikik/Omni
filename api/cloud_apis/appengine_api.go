package cloud_apis

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/api/appengine/v1"
)

// ==========================================
// 🚀 OMNI APP ENGINE — SERVERLESS LEGACY TARGET
// ==========================================
// App Engine memungkinkan deployment code murni tanpa mikirin Docker container.
// Digunakan OMNI untuk integrasi PaaS ke aplikasi monolithic.

type AppEngineBridge struct {
	projectID string
}

func NewAppEngineBridge(projectID string) *AppEngineBridge {
	return &AppEngineBridge{projectID: projectID}
}

// GetApplication mengambil root aplikasi App Engine (hanya ada 1 per project)
func (a *AppEngineBridge) GetApplication(ctx context.Context) (*appengine.Application, error) {
	svc, err := appengine.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPENGINE_ERROR: gagal membuat service: %v", err)
	}

	app, err := svc.Apps.Get(a.projectID).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPENGINE_ERROR: gagal mendapatkan detail aplikasi '%s': %v", a.projectID, err)
	}

	log.Printf("🚀 [OMNI APP ENGINE] Status: %s (Default Host: %s)", app.ServingStatus, app.DefaultHostname)
	return app, nil
}

// ListServices mengambil semua Microservices yang terdeploy di dalam App Engine
func (a *AppEngineBridge) ListServices(ctx context.Context) ([]*appengine.Service, error) {
	svc, err := appengine.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPENGINE_ERROR: gagal membuat service: %v", err)
	}

	resp, err := svc.Apps.Services.List(a.projectID).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPENGINE_ERROR: gagal list services: %v", err)
	}

	log.Printf("🚀 [OMNI APP ENGINE] Ditemukan %d services di project %s", len(resp.Services), a.projectID)
	return resp.Services, nil
}

// ListVersions mengambil semua versi di bawah satu service tertentu
func (a *AppEngineBridge) ListVersions(ctx context.Context, serviceId string) ([]*appengine.Version, error) {
	svc, err := appengine.NewService(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPENGINE_ERROR: gagal membuat service: %v", err)
	}

	resp, err := svc.Apps.Services.Versions.List(a.projectID, serviceId).Context(ctx).Do()
	if err != nil {
		return nil, fmt.Errorf("OMNI_APPENGINE_ERROR: gagal list versions untuk service '%s': %v", serviceId, err)
	}

	log.Printf("🚀 [OMNI APP ENGINE] Ditemukan %d versi untuk service %s", len(resp.Versions), serviceId)
	return resp.Versions, nil
}
