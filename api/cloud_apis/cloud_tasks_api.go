package cloud_apis

import (
	"context"
	"fmt"
	"log"

	cloudtasks "cloud.google.com/go/cloudtasks/apiv2"
	"cloud.google.com/go/cloudtasks/apiv2/cloudtaskspb"
)

// ==========================================
// ⏳ OMNI CLOUD TASKS — ASYNC TASK QUEUE
// ==========================================
// Cloud Tasks memungkinkan eksekusi asinkron terdistribusi.
//
// OMNI Framework menggunakan Cloud Tasks untuk:
//   - Penjadwalan webhook & notifikasi background
//   - Rate limiting untuk external API calls
//   - Guaranteed delivery untuk transaksi panjang
// ==========================================

// CloudTasksBridge menyediakan akses native ke Cloud Tasks
type CloudTasksBridge struct {
	projectID string
	location  string
	queueID   string
}

// NewCloudTasksBridge membuat bridge baru ke Cloud Tasks
func NewCloudTasksBridge(projectID, location, queueID string) *CloudTasksBridge {
	return &CloudTasksBridge{
		projectID: projectID,
		location:  location,
		queueID:   queueID,
	}
}

// queuePath menghasilkan fully-qualified queue path
func (t *CloudTasksBridge) queuePath() string {
	return fmt.Sprintf("projects/%s/locations/%s/queues/%s",
		t.projectID, t.location, t.queueID)
}

// CreateHttpTask membuat task baru dengan target HTTP URL
func (t *CloudTasksBridge) CreateHttpTask(ctx context.Context, url string, method cloudtaskspb.HttpMethod, body []byte) (*cloudtaskspb.Task, error) {
	client, err := cloudtasks.NewClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_TASKS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &cloudtaskspb.CreateTaskRequest{
		Parent: t.queuePath(),
		Task: &cloudtaskspb.Task{
			MessageType: &cloudtaskspb.Task_HttpRequest{
				HttpRequest: &cloudtaskspb.HttpRequest{
					HttpMethod: method,
					Url:        url,
					Body:       body,
					Headers: map[string]string{
						"Content-Type": "application/json",
						"X-Omni-Task":  "true",
					},
				},
			},
		},
	}

	createdTask, err := client.CreateTask(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_TASKS_ERROR: gagal membuat task: %v", err)
	}

	log.Printf("⏳ [OMNI CLOUD TASKS] Task HTTP berhasil dibuat: %s", createdTask.Name)
	return createdTask, nil
}

// PurgeQueue mengosongkan antrian (menghapus semua task di dalamnya)
func (t *CloudTasksBridge) PurgeQueue(ctx context.Context) error {
	client, err := cloudtasks.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("OMNI_TASKS_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	req := &cloudtaskspb.PurgeQueueRequest{
		Name: t.queuePath(),
	}

	_, err = client.PurgeQueue(ctx, req)
	if err != nil {
		return fmt.Errorf("OMNI_TASKS_ERROR: gagal purge queue: %v", err)
	}

	log.Printf("⏳ [OMNI CLOUD TASKS] Queue berhasil dibersihkan: %s", t.queueID)
	return nil
}
