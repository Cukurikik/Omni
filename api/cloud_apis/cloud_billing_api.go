package cloud_apis

import (
	"context"
	"fmt"

	billing "cloud.google.com/go/billing/apiv1"
	billingpb "cloud.google.com/go/billing/apiv1/billingpb"
	"google.golang.org/api/iterator"
)

// CloudBillingManager adalah wrapper OMNI-C/Rust Layer untuk GCP Cloud Billing
type CloudBillingManager struct {
	client *billing.CloudBillingClient
	ctx    context.Context
}

// NewCloudBillingManager menginisialisasi client Cloud Billing
func NewCloudBillingManager(ctx context.Context) (*CloudBillingManager, error) {
	client, err := billing.NewCloudBillingClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("omni.system.billing: gagal inisialisasi - %w", err)
	}

	return &CloudBillingManager{
		client: client,
		ctx:    ctx,
	}, nil
}

// Close membersihkan resource client
func (m *CloudBillingManager) Close() error {
	if m.client != nil {
		return m.client.Close()
	}
	return nil
}

// GetBillingAccount mendapatkan info tentang akun billing
func (m *CloudBillingManager) GetBillingAccount(billingAccountName string) (*billingpb.BillingAccount, error) {
	req := &billingpb.GetBillingAccountRequest{
		Name: fmt.Sprintf("billingAccounts/%s", billingAccountName),
	}

	acc, err := m.client.GetBillingAccount(m.ctx, req)
	if err != nil {
		return nil, fmt.Errorf("omni.billing.getAccount: %w", err)
	}

	return acc, nil
}

// ListProjectBillingInfo melist semua project yang terkait ke akun billing
func (m *CloudBillingManager) ListProjectBillingInfo(billingAccountName string) ([]*billingpb.ProjectBillingInfo, error) {
	req := &billingpb.ListProjectBillingInfoRequest{
		Name: fmt.Sprintf("billingAccounts/%s", billingAccountName),
	}

	var results []*billingpb.ProjectBillingInfo
	it := m.client.ListProjectBillingInfo(m.ctx, req)
	for {
		resp, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("omni.billing.listProjects: %w", err)
		}
		results = append(results, resp)
	}

	return results, nil
}

// DisableBilling secara otomatis (Kill Switch) jika ada anomali atau bug finansial
func (m *CloudBillingManager) DisableBilling(projectId string) (*billingpb.ProjectBillingInfo, error) {
	req := &billingpb.UpdateProjectBillingInfoRequest{
		Name: fmt.Sprintf("projects/%s", projectId),
		ProjectBillingInfo: &billingpb.ProjectBillingInfo{
			BillingAccountName: "", // Menghapus asosiasi billing account = disable billing
		},
	}

	resp, err := m.client.UpdateProjectBillingInfo(m.ctx, req)
	if err != nil {
		return nil, fmt.Errorf("omni.billing.disable: Kill Switch gagal diaktifkan - %w", err)
	}

	return resp, nil
}
