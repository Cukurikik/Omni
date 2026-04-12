package cloud_apis

import (
	"context"
	"fmt"

	cloudquotas "cloud.google.com/go/cloudquotas/apiv1"
	cloudquotaspb "cloud.google.com/go/cloudquotas/apiv1/cloudquotaspb"
	"google.golang.org/api/iterator"
)

// CloudQuotasManager adalah wrapper OMNI-C/Rust Layer untuk GCP Quotas
type CloudQuotasManager struct {
	client *cloudquotas.Client
	ctx    context.Context
}

// NewCloudQuotasManager menginisialisasi client Cloud Quotas
func NewCloudQuotasManager(ctx context.Context) (*CloudQuotasManager, error) {
	client, err := cloudquotas.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("omni.system.quotas: gagal inisialisasi - %w", err)
	}

	return &CloudQuotasManager{
		client: client,
		ctx:    ctx,
	}, nil
}

// Close membersihkan resource client
func (m *CloudQuotasManager) Close() error {
	if m.client != nil {
		return m.client.Close()
	}
	return nil
}

// GetQuotaInfo mengambil informasi detil dari suatu Quota
func (m *CloudQuotasManager) GetQuotaInfo(projectName string, serviceName string, quotaId string) (*cloudquotaspb.QuotaInfo, error) {
	// Format: projects/{project}/locations/global/services/{service}/quotaInfos/{quotaId}
	req := &cloudquotaspb.GetQuotaInfoRequest{
		Name: fmt.Sprintf("projects/%s/locations/global/services/%s/quotaInfos/%s", projectName, serviceName, quotaId),
	}

	info, err := m.client.GetQuotaInfo(m.ctx, req)
	if err != nil {
		return nil, fmt.Errorf("omni.quotas.get: gagal retrieve - %w", err)
	}

	return info, nil
}

// ListQuotaInfos melist banyak limit dari sebuah spesifik API/Service
func (m *CloudQuotasManager) ListQuotaInfos(projectName string, serviceName string) ([]*cloudquotaspb.QuotaInfo, error) {
	req := &cloudquotaspb.ListQuotaInfosRequest{
		Parent: fmt.Sprintf("projects/%s/locations/global/services/%s", projectName, serviceName),
	}

	var results []*cloudquotaspb.QuotaInfo
	it := m.client.ListQuotaInfos(m.ctx, req)
	for {
		resp, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("omni.quotas.list: list gagal - %w", err)
		}
		results = append(results, resp)
	}

	return results, nil
}

// UpdateQuotaPreference memperbarui rule/batasan secara dinamis (Edit Quota)
func (m *CloudQuotasManager) UpdateQuotaPreference(projectName string, preferenceId string, serviceName string, quotaId string, preferredValue int64) (*cloudquotaspb.QuotaPreference, error) {
	req := &cloudquotaspb.CreateQuotaPreferenceRequest{
		Parent:          fmt.Sprintf("projects/%s/locations/global", projectName),
		QuotaPreferenceId: preferenceId,
		QuotaPreference: &cloudquotaspb.QuotaPreference{
			Service: serviceName,
			QuotaId: quotaId,
			QuotaConfig: &cloudquotaspb.QuotaConfig{
				PreferredValue: preferredValue,
			},
		},
	}

	// Update quota requires calling Create on QuotaPreference API internally in GCP
	resp, err := m.client.CreateQuotaPreference(m.ctx, req)
	if err != nil {
		return nil, fmt.Errorf("omni.quotas.update: manipulasi quota ditolak di level GCP - %w", err)
	}

	return resp, nil
}
