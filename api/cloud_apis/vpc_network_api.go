package cloud_apis

import (
	"context"
	"fmt"

	compute "cloud.google.com/go/compute/apiv1"
	computepb "cloud.google.com/go/compute/apiv1/computepb"
	"google.golang.org/api/iterator"
)

// VPCNetworkManager adalah wrapper OMNI-C/Rust Layer untuk GCP VPC Network
type VPCNetworkManager struct {
	client *compute.NetworksClient
	ctx    context.Context
}

// NewVPCNetworkManager menginisialisasi client VPC
func NewVPCNetworkManager(ctx context.Context) (*VPCNetworkManager, error) {
	client, err := compute.NewNetworksRESTClient(ctx) // Compute Engine API typically uses REST client pattern in modern Go
	if err != nil {
		return nil, fmt.Errorf("omni.system.vpc: gagal inisialisasi - %w", err)
	}

	return &VPCNetworkManager{
		client: client,
		ctx:    ctx,
	}, nil
}

// Close membersihkan resource client
func (m *VPCNetworkManager) Close() error {
	if m.client != nil {
		return m.client.Close()
	}
	return nil
}

// ListNetworks melist semua VPC Network yang ada di pproject
func (m *VPCNetworkManager) ListNetworks(projectId string) ([]*computepb.Network, error) {
	req := &computepb.ListNetworksRequest{
		Project: projectId,
	}

	var results []*computepb.Network
	it := m.client.List(m.ctx, req)
	for {
		resp, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("omni.vpc.list: %w", err)
		}
		results = append(results, resp)
	}

	return results, nil
}

// GetNetwork mendapatkan info tentang VPC spesifik
func (m *VPCNetworkManager) GetNetwork(projectId string, networkName string) (*computepb.Network, error) {
	req := &computepb.GetNetworkRequest{
		Project: projectId,
		Network: networkName,
	}

	net, err := m.client.Get(m.ctx, req)
	if err != nil {
		return nil, fmt.Errorf("omni.vpc.get: %w", err)
	}

	return net, nil
}
