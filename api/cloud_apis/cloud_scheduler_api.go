package cloud_apis

import (
	"context"
	"fmt"
	"log"

	scheduler "cloud.google.com/go/scheduler/apiv1"
	"cloud.google.com/go/scheduler/apiv1/schedulerpb"
	"google.golang.org/api/iterator"
)

// ==========================================
// ⏰ OMNI CLOUD SCHEDULER — CRON JOB ENGINE
// ==========================================

type CloudSchedulerBridge struct {
	projectID string
	location  string
}

func NewCloudSchedulerBridge(projectID, location string) *CloudSchedulerBridge {
	return &CloudSchedulerBridge{projectID: projectID, location: location}
}

func (s *CloudSchedulerBridge) parentPath() string {
	return fmt.Sprintf("projects/%s/locations/%s", s.projectID, s.location)
}

func (s *CloudSchedulerBridge) ListJobs(ctx context.Context) ([]*schedulerpb.Job, error) {
	client, err := scheduler.NewCloudSchedulerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SCHEDULER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	it := client.ListJobs(ctx, &schedulerpb.ListJobsRequest{Parent: s.parentPath()})
	var jobs []*schedulerpb.Job
	for {
		job, err := it.Next()
		if err == iterator.Done {
			break
		}
		if err != nil {
			return nil, fmt.Errorf("OMNI_SCHEDULER_ERROR: gagal iterasi jobs: %v", err)
		}
		jobs = append(jobs, job)
	}
	log.Printf("⏰ [OMNI SCHEDULER] Ditemukan %d scheduled jobs", len(jobs))
	return jobs, nil
}

func (s *CloudSchedulerBridge) PauseJob(ctx context.Context, jobName string) (*schedulerpb.Job, error) {
	client, err := scheduler.NewCloudSchedulerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SCHEDULER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	job, err := client.PauseJob(ctx, &schedulerpb.PauseJobRequest{Name: jobName})
	if err != nil {
		return nil, fmt.Errorf("OMNI_SCHEDULER_ERROR: gagal pause job: %v", err)
	}
	log.Printf("⏰ [OMNI SCHEDULER] Job '%s' berhasil di-pause", jobName)
	return job, nil
}

func (s *CloudSchedulerBridge) RunJob(ctx context.Context, jobName string) (*schedulerpb.Job, error) {
	client, err := scheduler.NewCloudSchedulerClient(ctx)
	if err != nil {
		return nil, fmt.Errorf("OMNI_SCHEDULER_ERROR: gagal membuat client: %v", err)
	}
	defer client.Close()

	job, err := client.RunJob(ctx, &schedulerpb.RunJobRequest{Name: jobName})
	if err != nil {
		return nil, fmt.Errorf("OMNI_SCHEDULER_ERROR: gagal run job: %v", err)
	}
	log.Printf("⏰ [OMNI SCHEDULER] Job '%s' berhasil di-trigger", jobName)
	return job, nil
}
