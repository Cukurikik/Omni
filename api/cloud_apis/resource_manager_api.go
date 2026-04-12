package cloud_apis

import (
	"context"
	"fmt"
	"log"

	resourcemanager "cloud.google.com/go/resourcemanager/apiv3"
	"cloud.google.com/go/resourcemanager/apiv3/resourcemanagerpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 🏢 OMNI RESOURCE MANAGER — PROJECT/FOLDER/ORG MANAGEMENT
// ==========================================

type ResourceManagerBridge struct {
	projectID string
}

func NewResourceManagerBridge(projectID string) *ResourceManagerBridge {
	return &ResourceManagerBridge{projectID: projectID}
}

func (r *ResourceManagerBridge) GetProject(ctx context.Context) (*resourcemanagerpb.Project, error) {
	client, err := resourcemanager.NewProjectsClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_RESMGR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	project, err := client.GetProject(ctx, &resourcemanagerpb.GetProjectRequest{
		Name: fmt.Sprintf("projects/%s", r.projectID),
	})
	if err != nil {
		return nil, fmt.Errorf("OMNI_RESMGR_ERROR: gagal get project: %v", err)
	}
	log.Printf("🏢 [OMNI RESMGR] Project: %s (State: %s)", project.ProjectId, project.State)
	return project, nil
}

func (r *ResourceManagerBridge) SearchProjects(ctx context.Context, query string) ([]*resourcemanagerpb.Project, error) {
	client, err := resourcemanager.NewProjectsClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_RESMGR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.SearchProjects(ctx, &resourcemanagerpb.SearchProjectsRequest{Query: query})
	var projects []*resourcemanagerpb.Project
	for {
		p, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_RESMGR_ERROR: gagal search: %v", err)
		}
		projects = append(projects, p)
	}
	log.Printf("🏢 [OMNI RESMGR] Ditemukan %d projects", len(projects))
	return projects, nil
}
