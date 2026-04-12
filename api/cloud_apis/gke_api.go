package cloud_apis

import (
	"context"
	"fmt"
	"log"

	container "cloud.google.com/go/container/apiv1"
	"cloud.google.com/go/container/apiv1/containerpb"
)

// ==========================================
// ☸️ OMNI GKE — KUBERNETES ENGINE
// ==========================================

type GKEBridge struct {
	projectID string
	location  string
}

func NewGKEBridge(projectID, location string) *GKEBridge {
	return &GKEBridge{projectID: projectID, location: location}
}

func (g *GKEBridge) parentPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", g.projectID, g.location)
}

func (g *GKEBridge) ListClusters(ctx context.Context) ([]*containerpb.Cluster, error) {
	client, err := container.NewClusterManagerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	resp, err := client.ListClusters(ctx, &containerpb.ListClustersRequest{Parent: g.parentPath()})
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal list clusters: %v", err)
	}
	log.Printf("☸️ [OMNI GKE] Ditemukan %d clusters", len(resp.Clusters))
	return resp.Clusters, nil
}

func (g *GKEBridge) GetCluster(ctx context.Context, clusterName string) (*containerpb.Cluster, error) {
	client, err := container.NewClusterManagerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("%s/clusters/%s", g.parentPath(), clusterName)
	cluster, err := client.GetCluster(ctx, &containerpb.GetClusterRequest{Name: name})
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal get cluster '%s': %v", clusterName, err)
	}
	log.Printf("☸️ [OMNI GKE] Cluster: %s (Status: %s, Nodes: %d)", cluster.Name, cluster.Status, cluster.CurrentNodeCount)
	return cluster, nil
}

// ==========================================
// EXPANSION: NODE POOLS, WORKLOADS, SERVICES & INGRESS (Wave 12)
// ==========================================

// ListNodePools mengambil seluruh Node Pool yang berjalan di sebuah Cluster
func (g *GKEBridge) ListNodePools(ctx context.Context, clusterName string) ([]*containerpb.NodePool, error) {
	client, err := container.NewClusterManagerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	parent := fmt.Sprintf("%s/clusters/%s", g.parentPath(), clusterName)
	resp, err := client.ListNodePools(ctx, &containerpb.ListNodePoolsRequest{Parent: parent})
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal list node pools untuk '%s': %v", clusterName, err)
	}
	log.Printf("☸️ [OMNI GKE] Ditemukan %d node pools di cluster '%s'", len(resp.NodePools), clusterName)
	return resp.NodePools, nil
}

// DeleteCluster menghancurkan sebuah cluster GKE secara otonom
func (g *GKEBridge) DeleteCluster(ctx context.Context, clusterName string) error {
	client, err := container.NewClusterManagerClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_GKE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("%s/clusters/%s", g.parentPath(), clusterName)
	_, err = client.DeleteCluster(ctx, &containerpb.DeleteClusterRequest{Name: name})
	if err != nil {
		return fmt.Errorf("OMNI_GKE_ERROR: gagal menghapus cluster '%s': %v", clusterName, err)
	}
	log.Printf("☸️ [OMNI GKE] Cluster '%s' sedang dimusnahkan (deletion queued)", clusterName)
	return nil
}

// GetServerConfig mengambil konfigurasi server K8s (versi stabil, channel, dll.)
func (g *GKEBridge) GetServerConfig(ctx context.Context) (*containerpb.ServerConfig, error) {
	client, err := container.NewClusterManagerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("projects/%s/locations/%s", g.projectID, g.location)
	cfg, err := client.GetServerConfig(ctx, &containerpb.GetServerConfigRequest{Name: name})
	if err != nil {
		return nil, fmt.Errorf("OMNI_GKE_ERROR: gagal get server config: %v", err)
	}
	log.Printf("☸️ [OMNI GKE] K8s default version: %s", cfg.DefaultClusterVersion)
	return cfg, nil
}

// OmniK8sWorkload merepresentasikan ringkasan beban kerja pada cluster (Adapter pattern)
type OmniK8sWorkload struct {
	Name       string `json:"name"`
	Namespace  string `json:"namespace"`
	Type       string `json:"type"`   // Deployment, StatefulSet, DaemonSet
	Replicas   int32  `json:"replicas"`
	Status     string `json:"status"` // Ready, Pending, Failed
}

// OmniK8sService merepresentasikan ringkasan Layanan (Service) K8s
type OmniK8sService struct {
	Name       string `json:"name"`
	Namespace  string `json:"namespace"`
	Type       string `json:"type"`       // ClusterIP, NodePort, LoadBalancer
	ClusterIP  string `json:"cluster_ip"`
	ExternalIP string `json:"external_ip,omitempty"`
}

// OmniK8sIngress merepresentasikan ringkasan Ingress rule
type OmniK8sIngress struct {
	Name       string   `json:"name"`
	Namespace  string   `json:"namespace"`
	Hosts      []string `json:"hosts"`
	Address    string   `json:"address,omitempty"`
}
