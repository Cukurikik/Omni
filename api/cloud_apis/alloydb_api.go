package cloud_apis

import (
	"context"
	"fmt"
	"log"

	alloydb "cloud.google.com/go/alloydb/apiv1"
	"cloud.google.com/go/alloydb/apiv1/alloydbpb"
)

// ==========================================
// 🐘 OMNI ALLOYDB — POSTGRESQL FOR ENTERPRISE
// ==========================================
// AlloyDB adalah database relasional yang fully compatible dengan PostgreSQL,
// namun 4x lebih cepat untuk transactional (OLTP) dan 100x analitik (OLAP).
//
// OMNI Framework menggunakan AlloyDB untuk:
//   - Hybrid Transactional and Analytical Processing (HTAP)
//   - High-throughput Postgres workloads
//   - AI embedding vector search pgvector scale up
// ==========================================

// AlloyDBBridge memberikan akses native kontrol ke AlloyDB
type AlloyDBBridge struct {
	projectID string
	location  string
	cluster   string
}

// NewAlloyDBBridge membuat instance bridge baru
func NewAlloyDBBridge(projectID, location, cluster string) *AlloyDBBridge {
	return &AlloyDBBridge{
		projectID: projectID,
		location:  location,
		cluster:   cluster,
	}
}

// clusterPath menghasilkan cluster path yang fully-qualified
func (a *AlloyDBBridge) clusterPath() string {
	return fmt.Sprintf("projects/%s/locations/%s/clusters/%s", a.projectID, a.location, a.cluster)
}

// GetClusterInfo mengambil metadata dari cluster AlloyDB
func (a *AlloyDBBridge) GetClusterInfo(ctx context.Context) (*alloydbpb.Cluster, error) {
	client, err := alloydb.NewAlloyDBAdminClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ALLOYDB_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &alloydbpb.GetClusterRequest{
		Name: a.clusterPath(),
	}

	cluster, err := client.GetCluster(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_ALLOYDB_ERROR: gagal mendapatkan info cluster: %v", err)
	}

	state := cluster.State
	log.Printf("🐘 [OMNI ALLOYDB] Info Cluster '%s' ditarik. State: %v", cluster.Name, state)
	return cluster, nil
}
