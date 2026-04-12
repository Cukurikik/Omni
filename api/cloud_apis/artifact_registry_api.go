package cloud_apis

import (
	"context"
	"fmt"
	"log"

	artifactregistry "cloud.google.com/go/artifactregistry/apiv1"
	"cloud.google.com/go/artifactregistry/apiv1/artifactregistrypb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 📦 OMNI ARTIFACT REGISTRY — Container & Package Registry
// ==========================================
// Artifact Registry menyimpan Docker images, npm packages,
// Maven artifacts, dan lainnya secara terkelola di GCP.
//
// OMNI Framework menggunakan Artifact Registry untuk:
//   - Menyimpan Docker images hasil build Cloud Build
//   - Distribusi OMNI packages via npm/Go/Python registries
//   - Version management untuk semua deployment artifacts
//   - Vulnerability scanning untuk container images
//
// Target ARR: Model C — PaaS Infrastructure
// ==========================================

// ArtifactRegistryBridge menyediakan akses ke Artifact Registry
type ArtifactRegistryBridge struct {
	projectID string
	location  string
}

// NewArtifactRegistryBridge membuat bridge baru ke Artifact Registry
func NewArtifactRegistryBridge(projectID, location string) *ArtifactRegistryBridge {
	return &ArtifactRegistryBridge{
		projectID: projectID,
		location:  location,
	}
}

// ListRepositories mengambil daftar semua repositories di project/location
func (a *ArtifactRegistryBridge) ListRepositories(ctx context.Context) ([]*artifactregistrypb.Repository, error) {
	client, err := artifactregistry.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ARTIFACT_REGISTRY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	parent := fmt.Sprintf("projects/%s/locations/%s", a.projectID, a.location)
	req := &artifactregistrypb.ListRepositoriesRequest{
		Parent: parent,
	}

	it := client.ListRepositories(ctx, req)
	var repos []*artifactregistrypb.Repository
	for {
		repo, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_ARTIFACT_REGISTRY_ERROR: gagal iterasi repositories: %v", err)
		}
		repos = append(repos, repo)
	}

	log.Printf("📦 [OMNI ARTIFACT REGISTRY] Ditemukan %d repositories di '%s'", len(repos), parent)
	return repos, nil
}

// GetRepository mengambil detail satu repository
func (a *ArtifactRegistryBridge) GetRepository(ctx context.Context, repoName string) (*artifactregistrypb.Repository, error) {
	client, err := artifactregistry.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ARTIFACT_REGISTRY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("projects/%s/locations/%s/repositories/%s", a.projectID, a.location, repoName)
	req := &artifactregistrypb.GetRepositoryRequest{
		Name: name,
	}

	repo, err := client.GetRepository(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ARTIFACT_REGISTRY_ERROR: gagal mengambil repo '%s': %v", repoName, err)
	}

	log.Printf("📦 [OMNI ARTIFACT REGISTRY] Repository: %s (Format: %s)", repo.Name, repo.Format)
	return repo, nil
}

// ListDockerImages mengambil daftar Docker images di sebuah repository
func (a *ArtifactRegistryBridge) ListDockerImages(ctx context.Context, repoName string) ([]*artifactregistrypb.DockerImage, error) {
	client, err := artifactregistry.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ARTIFACT_REGISTRY_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	parent := fmt.Sprintf("projects/%s/locations/%s/repositories/%s", a.projectID, a.location, repoName)
	req := &artifactregistrypb.ListDockerImagesRequest{
		Parent: parent,
	}

	it := client.ListDockerImages(ctx, req)
	var images []*artifactregistrypb.DockerImage
	count := 0
	for {
		img, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_ARTIFACT_REGISTRY_ERROR: gagal iterasi images: %v", err)
		}
		images = append(images, img)
		count++
		if count >= 100 { // Limit output
			break
		}
	}

	log.Printf("📦 [OMNI ARTIFACT REGISTRY] Ditemukan %d Docker images di '%s'", len(images), repoName)
	return images, nil
}
