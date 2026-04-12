package cloud_apis

import (
	"context"
	"fmt"
	"log"

	run "cloud.google.com/go/run/apiv2"
	"cloud.google.com/go/run/apiv2/runpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🚀 OMNI CLOUD RUN — SERVERLESS CONTAINERS
// ==========================================
// Cloud Run menjalankan container tanpa perlu mengelola server.
//
// OMNI Framework menggunakan Cloud Run untuk:
//   - Deploy OMNI microservices (Go, Rust, Python)
//   - Auto-scaling 0-to-N untuk OMNI Cloud PaaS
//   - Unikernel deployment target
//   - API Gateway backend
//
// Target ARR: inti dari PaaS Cloud Hosting tier $29/bulan
// ==========================================

// CloudRunBridge menyediakan akses native ke Cloud Run Services
type CloudRunBridge struct {
	projectID string
	location  string
}

// NewCloudRunBridge membuat bridge baru ke Cloud Run
func NewCloudRunBridge(projectID, location string) *CloudRunBridge {
	return &CloudRunBridge{
		projectID: projectID,
		location:  location,
	}
}

// locationPath menghasilkan fully-qualified location path
func (c *CloudRunBridge) locationPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", c.projectID, c.location)
}

// ListServices mengambil daftar semua Cloud Run services di region
func (c *CloudRunBridge) ListServices(ctx context.Context) ([]*runpb.Service, error) {
	client, err := run.NewServicesClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &runpb.ListServicesRequest{
		Parent: c.locationPath(),
	}

	it := client.ListServices(ctx, req)
	var services []*runpb.Service
	for {
		svc, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal iterasi services: %v", err)
		}
		services = append(services, svc)
	}

	log.Printf("🚀 [OMNI CLOUD RUN] Ditemukan %d services di %s", len(services), c.location)
	return services, nil
}

// GetService mengambil detail satu Cloud Run service
func (c *CloudRunBridge) GetService(ctx context.Context, serviceName string) (*runpb.Service, error) {
	client, err := run.NewServicesClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("%s/services/%s", c.locationPath(), serviceName)
	req := &runpb.GetServiceRequest{
		Name: name,
	}

	svc, err := client.GetService(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal mengambil service '%s': %v", serviceName, err)
	}

	log.Printf("🚀 [OMNI CLOUD RUN] Service ditemukan: %s (URI: %s)", svc.Name, svc.Uri)
	return svc, nil
}

// DeleteService menghapus Cloud Run service
func (c *CloudRunBridge) DeleteService(ctx context.Context, serviceName string) error {
	client, err := run.NewServicesClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("%s/services/%s", c.locationPath(), serviceName)
	req := &runpb.DeleteServiceRequest{
		Name: name,
	}

	op, err := client.DeleteService(ctx, req)
	if err != nil {
		return fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal menghapus service '%s': %v", serviceName, err)
	}

	_, err = op.Wait(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal menunggu penghapusan '%s': %v", serviceName, err)
	}

	log.Printf("🚀 [OMNI CLOUD RUN] Service '%s' berhasil dihapus", serviceName)
	return nil
}

// ListRevisions mengambil daftar revision untuk sebuah service
func (c *CloudRunBridge) ListRevisions(ctx context.Context, serviceName string) ([]*runpb.Revision, error) {
	client, err := run.NewRevisionsClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal membuat revisions client: %v", err)
	}
	defer client.Close()

	req := &runpb.ListRevisionsRequest{
		Parent: fmt.Sprintf("%s/services/%s", c.locationPath(), serviceName),
	}

	it := client.ListRevisions(ctx, req)
	var revisions []*runpb.Revision
	for {
		rev, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal iterasi revisions: %v", err)
		}
		revisions = append(revisions, rev)
	}

	log.Printf("🚀 [OMNI CLOUD RUN] Ditemukan %d revisions untuk '%s'", len(revisions), serviceName)
	return revisions, nil
}

// CreateService membuat Cloud Run service baru secara otonom (OMNI PaaS Bridge)
func (c *CloudRunBridge) CreateService(ctx context.Context, serviceName, imageURI string, port int32) error {
	client, err := run.NewServicesClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	// Mengamankan port agar OMNI Cloud selalu kompatibel dengan Zero-Trust architecture
	if port == 0 {
		port = 8080
	}

	req := &runpb.CreateServiceRequest{
		Parent:    c.locationPath(),
		ServiceId: serviceName,
		Service: &runpb.Service{
			Template: &runpb.RevisionTemplate{
				Containers: []*runpb.Container{
					{
						Image: imageURI,
						Ports: []*runpb.ContainerPort{
							{ContainerPort: port},
						},
					},
				},
			},
		},
	}

	op, err := client.CreateService(ctx, req)
	if err != nil {
		return fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal mengirim command CreateService '%s': %v", serviceName, err)
	}

	_, err = op.Wait(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_CLOUDRUN_ERROR: gagal menunggu pembuatan service '%s': %v", serviceName, err)
	}

	log.Printf("🚀 [OMNI CLOUD RUN] Service '%s' (Image: %s) berhasil di-deploy ke PaaS!", serviceName, imageURI)
	return nil
}
