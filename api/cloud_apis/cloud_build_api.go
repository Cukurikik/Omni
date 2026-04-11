package cloud_apis

import (
	"context"
	"fmt"
	"log"

	cloudbuild "cloud.google.com/go/cloudbuild/apiv1/v2"
	"cloud.google.com/go/cloudbuild/apiv1/v2/cloudbuildpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🔨 OMNI CLOUD BUILD — CI/CD PIPELINE
// ==========================================
// Cloud Build menjalankan build steps secara terkelola di GCP.
//
// OMNI Framework menggunakan Cloud Build untuk:
//   - CI/CD pipeline untuk setiap push ke GitHub
//   - Multi-architecture build (x86_64, aarch64, WASM)
//   - Docker image build untuk Cloud Run deployment
//   - OMNI LLVM compilation pipeline
//
// Target ARR: bagian dari DevOps tier
// ==========================================

// CloudBuildBridge menyediakan akses ke Cloud Build
type CloudBuildBridge struct {
	projectID string
	location  string
}

// NewCloudBuildBridge membuat bridge baru ke Cloud Build
func NewCloudBuildBridge(projectID, location string) *CloudBuildBridge {
	return &CloudBuildBridge{
		projectID: projectID,
		location:  location,
	}
}

// ListBuilds mengambil daftar semua builds di project
func (b *CloudBuildBridge) ListBuilds(ctx context.Context) ([]*cloudbuildpb.Build, error) {
	client, err := cloudbuild.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDBUILD_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &cloudbuildpb.ListBuildsRequest{
		ProjectId: b.projectID,
	}

	it := client.ListBuilds(ctx, req)
	var builds []*cloudbuildpb.Build
	count := 0
	for {
		build, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_CLOUDBUILD_ERROR: gagal iterasi builds: %v", err)
		}
		builds = append(builds, build)
		count++
		if count >= 50 { // Limit ke 50 untuk performa
			break
		}
	}

	log.Printf("🔨 [OMNI CLOUD BUILD] Ditemukan %d builds di project '%s'", len(builds), b.projectID)
	return builds, nil
}

// GetBuild mengambil detail satu build berdasarkan ID
func (b *CloudBuildBridge) GetBuild(ctx context.Context, buildID string) (*cloudbuildpb.Build, error) {
	client, err := cloudbuild.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDBUILD_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &cloudbuildpb.GetBuildRequest{
		ProjectId: b.projectID,
		Id:        buildID,
	}

	build, err := client.GetBuild(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDBUILD_ERROR: gagal mengambil build '%s': %v", buildID, err)
	}

	log.Printf("🔨 [OMNI CLOUD BUILD] Build ditemukan: %s (Status: %s)", build.Id, build.Status)
	return build, nil
}

// CancelBuild membatalkan build yang sedang berjalan
func (b *CloudBuildBridge) CancelBuild(ctx context.Context, buildID string) (*cloudbuildpb.Build, error) {
	client, err := cloudbuild.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDBUILD_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &cloudbuildpb.CancelBuildRequest{
		ProjectId: b.projectID,
		Id:        buildID,
	}

	build, err := client.CancelBuild(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_CLOUDBUILD_ERROR: gagal membatalkan build '%s': %v", buildID, err)
	}

	log.Printf("🔨 [OMNI CLOUD BUILD] Build '%s' berhasil dibatalkan", build.Id)
	return build, nil
}
