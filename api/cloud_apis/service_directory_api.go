package cloud_apis

import (
	"context"
	"fmt"
	"log"

	servicedirectory "cloud.google.com/go/servicedirectory/apiv1"
	"cloud.google.com/go/servicedirectory/apiv1/servicedirectorypb"
	"google.golang.org/api/iterator"
)

// ==========================================
// 📖 OMNI SERVICE DIRECTORY — SERVICE DISCOVERY
// ==========================================

type ServiceDirectoryBridge struct {
	projectID string
	location  string
}

func NewServiceDirectoryBridge(projectID, location string) *ServiceDirectoryBridge {
	return &ServiceDirectoryBridge{projectID: projectID, location: location}
}

func (s *ServiceDirectoryBridge) parentPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", s.projectID, s.location)
}

func (s *ServiceDirectoryBridge) ListNamespaces(ctx context.Context) ([]*servicedirectorypb.Namespace, error) {
	client, err := servicedirectory.NewRegistrationClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SVCDIR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListNamespaces(ctx, &servicedirectorypb.ListNamespacesRequest{Parent: s.parentPath()})
	var namespaces []*servicedirectorypb.Namespace
	for {
		ns, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_SVCDIR_ERROR: gagal iterasi: %v", err)
		}
		namespaces = append(namespaces, ns)
	}
	log.Printf("📖 [OMNI SERVICE DIR] Ditemukan %d namespaces", len(namespaces))
	return namespaces, nil
}

func (s *ServiceDirectoryBridge) ListServices(ctx context.Context, namespaceName string) ([]*servicedirectorypb.Service, error) {
	client, err := servicedirectory.NewRegistrationClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SVCDIR_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListServices(ctx, &servicedirectorypb.ListServicesRequest{Parent: namespaceName})
	var services []*servicedirectorypb.Service
	for {
		svc, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_SVCDIR_ERROR: gagal iterasi services: %v", err)
		}
		services = append(services, svc)
	}
	log.Printf("📖 [OMNI SERVICE DIR] Ditemukan %d services", len(services))
	return services, nil
}
