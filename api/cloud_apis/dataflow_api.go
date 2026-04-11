package cloud_apis

import (
	"context"
	"fmt"
	"log"

	dataflow "cloud.google.com/go/dataflow/apiv1beta3"
	"cloud.google.com/go/dataflow/apiv1beta3/dataflowpb"
)

// ==========================================
// 🌊 OMNI DATAFLOW — REAL-TIME STREAM PROCESSING
// ==========================================
// Cloud Dataflow (Apache Beam) memproses data streaming dan batch
// dalam skala petabyte tanpa manajemen server.
//
// Untuk OMNI:
//   - HFT tick data processing (Julia SIMD → Dataflow → BigQuery)
//   - Real-time telemetry aggregation dari OMNI-Swarm nodes
//   - ETL pipeline: Pub/Sub → Transform → BigQuery/Spanner
//
// Target ARR: +$60.000 via Enterprise Streaming Tier
// ==========================================

// DataflowBridge menyediakan akses native ke Cloud Dataflow
type DataflowBridge struct {
	projectID string
	region    string
}

// NewDataflowBridge membuat bridge baru
func NewDataflowBridge(projectID, region string) *DataflowBridge {
	return &DataflowBridge{
		projectID: projectID,
		region:    region,
	}
}

// LaunchTemplate meluncurkan Dataflow job dari template yang sudah ada
// Ini adalah cara tercepat untuk men-deploy pipeline streaming
func (d *DataflowBridge) LaunchTemplate(ctx context.Context, jobName, templatePath string, parameters map[string]string) (string, error) {
	client, err := dataflow.NewTemplatesClient(ctx)
	if err != nil {
		return "", fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal membuat templates client: %v", err)
	}
	defer client.Close()

	req := &dataflowpb.LaunchTemplateRequest{
		ProjectId: d.projectID,
		Location:  d.region,
		Template: &dataflowpb.LaunchTemplateRequest_GcsPath{
			GcsPath: templatePath,
		},
		LaunchParameters: &dataflowpb.LaunchTemplateParameters{
			JobName:    jobName,
			Parameters: parameters,
		},
	}

	resp, err := client.LaunchTemplate(ctx, req)
	if err != nil {
		return "", fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal meluncurkan template: %v", err)
	}

	jobID := resp.GetJob().GetId()
	log.Printf("🌊 [OMNI DATAFLOW] Job berhasil diluncurkan: %s (ID: %s)", jobName, jobID)
	return jobID, nil
}

// LaunchFlexTemplate meluncurkan Flex Template (custom container image)
// Lebih fleksibel — bisa menggunakan OMNI Unikernel sebagai worker
func (d *DataflowBridge) LaunchFlexTemplate(ctx context.Context, jobName, templatePath string, parameters map[string]string) (string, error) {
	client, err := dataflow.NewFlexTemplatesClient(ctx)
	if err != nil {
		return "", fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal membuat flex templates client: %v", err)
	}
	defer client.Close()

	req := &dataflowpb.LaunchFlexTemplateRequest{
		ProjectId: d.projectID,
		Location:  d.region,
		LaunchParameter: &dataflowpb.LaunchFlexTemplateParameter{
			JobName: jobName,
			Template: &dataflowpb.LaunchFlexTemplateParameter_ContainerSpecGcsPath{
				ContainerSpecGcsPath: templatePath,
			},
			Parameters: parameters,
		},
	}

	resp, err := client.LaunchFlexTemplate(ctx, req)
	if err != nil {
		return "", fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal meluncurkan flex template: %v", err)
	}

	jobID := resp.GetJob().GetId()
	log.Printf("🌊 [OMNI DATAFLOW] Flex Job berhasil diluncurkan: %s (ID: %s)", jobName, jobID)
	return jobID, nil
}

// ListJobs menampilkan semua Dataflow jobs yang sedang berjalan
func (d *DataflowBridge) ListJobs(ctx context.Context) ([]*DataflowJobInfo, error) {
	client, err := dataflow.NewJobsV1Beta3Client(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal membuat jobs client: %v", err)
	}
	defer client.Close()

	req := &dataflowpb.ListJobsRequest{
		ProjectId: d.projectID,
		Location:  d.region,
	}

	var jobs []*DataflowJobInfo
	it := client.ListJobs(ctx, req)
	for {
		job, err := it.Next()
		if err != nil {
			break
		}
		jobs = append(jobs, &DataflowJobInfo{
			ID:     job.GetId(),
			Name:   job.GetName(),
			State:  job.GetCurrentState().String(),
			Type:   job.GetType().String(),
		})
	}

	log.Printf("🌊 [OMNI DATAFLOW] Ditemukan %d jobs di region %s", len(jobs), d.region)
	return jobs, nil
}

// GetJob mengambil detail job berdasarkan ID
func (d *DataflowBridge) GetJob(ctx context.Context, jobID string) (*DataflowJobInfo, error) {
	client, err := dataflow.NewJobsV1Beta3Client(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal membuat jobs client: %v", err)
	}
	defer client.Close()

	req := &dataflowpb.GetJobRequest{
		ProjectId: d.projectID,
		Location:  d.region,
		JobId:     jobID,
	}

	job, err := client.GetJob(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("OMNI_DATAFLOW_ERROR: gagal mengambil job %s: %v", jobID, err)
	}

	log.Printf("🌊 [OMNI DATAFLOW] Job %s status: %s", jobID, job.GetCurrentState().String())
	return &DataflowJobInfo{
		ID:    job.GetId(),
		Name:  job.GetName(),
		State: job.GetCurrentState().String(),
		Type:  job.GetType().String(),
	}, nil
}

// DataflowJobInfo berisi informasi ringkas tentang Dataflow job
type DataflowJobInfo struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	State string `json:"state"`
	Type  string `json:"type"`
}
