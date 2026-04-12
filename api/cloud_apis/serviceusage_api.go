package cloud_apis

import (
	"context"
	"fmt"

	serviceusage "cloud.google.com/go/serviceusage/apiv1"
	serviceusagepb "cloud.google.com/go/serviceusage/apiv1/serviceusagepb"
	"google.golang.org/api/iterator"
)

// ServiceUsageManager adalah wrapper OMNI-C/Rust Layer untuk GCP Service Usage
type ServiceUsageManager struct {
	client *serviceusage.Client
	ctx    context.Context
}

// NewServiceUsageManager menginisialisasi client Service Usage
func NewServiceUsageManager(ctx context.Context) (*ServiceUsageManager, error) {
	client, err := serviceusage.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("omni.system.serviceusage: gagal inisialisasi - %w", err)
	}

	return &ServiceUsageManager{
		client: client,
		ctx:    ctx,
	}, nil
}

// Close membersihkan resource client
func (m *ServiceUsageManager) Close() error {
	if m.client != nil {
		return m.client.Close()
	}
	return nil
}

// ListEnabledServices melist service GCP yang diaktifkan di project (misal dari 1775)
func (m *ServiceUsageManager) ListEnabledServices(projectName string) ([]*serviceusagepb.Service, error) {
	req := &serviceusagepb.ListServicesRequest{
		Parent: fmt.Sprintf("projects/%s", projectName),
		Filter: "state:ENABLED",
	}

	var results []*serviceusagepb.Service
	it := m.client.ListServices(m.ctx, req)
	for {
		resp, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("omni.serviceusage.list: gagal mengiterasi service - %w", err)
		}
		results = append(results, resp)
	}

	return results, nil
}

// GetService mengecek status 1 service API spesifik (misal apakah AI Platform aktif)
func (m *ServiceUsageManager) GetService(projectName string, serviceName string) (*serviceusagepb.Service, error) {
	req := &serviceusagepb.GetServiceRequest{
		Name: fmt.Sprintf("projects/%s/services/%s", projectName, serviceName),
	}

	resp, err := m.client.GetService(m.ctx, req)
	if err != nil {
		return nil, fmt.Errorf("omni.serviceusage.get: tidak menemukan service - %w", err)
	}

	return resp, nil
}

// EnableService mengaktifkan service di GCP secara dinamis dari Telepathy Engine OMNI
func (m *ServiceUsageManager) EnableService(projectName string, serviceName string) error {
	req := &serviceusagepb.EnableServiceRequest{
		Name: fmt.Sprintf("projects/%s/services/%s", projectName, serviceName),
	}

	op, err := m.client.EnableService(m.ctx, req)
	if err != nil {
		return fmt.Errorf("omni.serviceusage.enable: request ditolak GCP - %w", err)
	}

	_, err = op.Wait(m.ctx)
	if err != nil {
		return fmt.Errorf("omni.serviceusage.enable: proses async gagal di GCP side - %w", err)
	}

	return nil
}

// DisableService mematikan service
func (m *ServiceUsageManager) DisableService(projectName string, serviceName string) error {
	req := &serviceusagepb.DisableServiceRequest{
		Name: fmt.Sprintf("projects/%s/services/%s", projectName, serviceName),
	}

	op, err := m.client.DisableService(m.ctx, req)
	if err != nil {
		return fmt.Errorf("omni.serviceusage.disable: request ditolak GCP - %w", err)
	}

	_, err = op.Wait(m.ctx)
	if err != nil {
		return fmt.Errorf("omni.serviceusage.disable: proses async gagal - %w", err)
	}

	return nil
}
