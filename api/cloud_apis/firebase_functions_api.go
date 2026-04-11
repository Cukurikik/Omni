package cloud_apis

import (
	"context"
	"fmt"
	"log"

	functions "cloud.google.com/go/functions/apiv2"
	"cloud.google.com/go/functions/apiv2/functionspb"
	"google.golang.org/api/iterator"
)

// ==========================================
// ⚙️ OMNI CLOUD FUNCTIONS — SERVERLESS COMPUTE
// ==========================================
// Cloud Functions menyediakan serverless execution environment.
//
// OMNI Framework menggunakan Cloud Functions untuk:
//   - Event-driven microservices (Firestore triggers, Pub/Sub)
//   - Lightweight API endpoints tanpa server management
//   - Scheduled tasks (cron jobs serverless)
//   - Firebase Extension runners
//
// Target ARR: bagian dari PaaS tier $29/bulan
// ==========================================

// CloudFunctionsBridge menyediakan akses ke Cloud Functions (Gen 2)
type CloudFunctionsBridge struct {
	projectID string
	location  string
}

// NewCloudFunctionsBridge membuat bridge baru ke Cloud Functions
func NewCloudFunctionsBridge(projectID, location string) *CloudFunctionsBridge {
	return &CloudFunctionsBridge{
		projectID: projectID,
		location:  location,
	}
}

// locationPath menghasilkan fully-qualified location path
func (c *CloudFunctionsBridge) locationPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", c.projectID, c.location)
}

// ListFunctions mengambil daftar semua Cloud Functions di region yang ditentukan
func (c *CloudFunctionsBridge) ListFunctions(ctx context.Context) ([]*functionspb.Function, error) {
	client, err := functions.NewFunctionClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &functionspb.ListFunctionsRequest{
		Parent: c.locationPath(),
	}

	it := client.ListFunctions(ctx, req)
	var funcs []*functionspb.Function
	for {
		fn, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal iterasi functions: %v", err)
		}
		funcs = append(funcs, fn)
	}

	log.Printf("⚙️ [OMNI FUNCTIONS] Ditemukan %d functions di %s", len(funcs), c.location)
	return funcs, nil
}

// GetFunction mengambil detail satu Cloud Function berdasarkan nama
func (c *CloudFunctionsBridge) GetFunction(ctx context.Context, functionName string) (*functionspb.Function, error) {
	client, err := functions.NewFunctionClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("%s/functions/%s", c.locationPath(), functionName)
	req := &functionspb.GetFunctionRequest{
		Name: name,
	}

	fn, err := client.GetFunction(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal mengambil function '%s': %v", functionName, err)
	}

	log.Printf("⚙️ [OMNI FUNCTIONS] Function ditemukan: %s (State: %s)", fn.Name, fn.State)
	return fn, nil
}

// DeleteFunction menghapus Cloud Function berdasarkan nama
func (c *CloudFunctionsBridge) DeleteFunction(ctx context.Context, functionName string) error {
	client, err := functions.NewFunctionClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	name := fmt.Sprintf("%s/functions/%s", c.locationPath(), functionName)
	req := &functionspb.DeleteFunctionRequest{
		Name: name,
	}

	op, err := client.DeleteFunction(ctx, req)
	if err != nil {
		return fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal menghapus function '%s': %v", functionName, err)
	}

	err = op.Wait(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_FUNCTIONS_ERROR: gagal menunggu penghapusan '%s': %v", functionName, err)
	}

	log.Printf("⚙️ [OMNI FUNCTIONS] Function '%s' berhasil dihapus", functionName)
	return nil
}
