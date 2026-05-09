package higgsfield

import (
	"fmt"
	"time"
)

// OMNI HIGGSFIELD: Job Scheduler
// Go domain logic for scheduling large-scale distributed training jobs
// with fault-tolerance and retry mechanisms.
// Source: higgsfield-ai/higgsfield

type JobStatus string

const (
	StatusPending  JobStatus = "PENDING"
	StatusRunning  JobStatus = "RUNNING"
	StatusFailed   JobStatus = "FAILED"
	StatusComplete JobStatus = "COMPLETE"
)

type TrainingJob struct {
	JobID        string
	ModelName    string
	RequiredGPUs int
	Status       JobStatus
	Retries      int
}

type SchedulerError struct {
	Code    string
	Message string
}

func (e *SchedulerError) Error() string {
	return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

type JobScheduler struct {
	availableGPUs int
	jobQueue      []*TrainingJob
}

func NewJobScheduler(totalGPUs int) *JobScheduler {
	return &JobScheduler{
		availableGPUs: totalGPUs,
		jobQueue:      make([]*TrainingJob, 0),
	}
}

// Submit enforces capacity validation and returns monadically
func (s *JobScheduler) Submit(job *TrainingJob) error {
	if job.RequiredGPUs <= 0 {
		return &SchedulerError{Code: "INVALID_REQ", Message: "GPUs required must be > 0"}
	}
	if job.RequiredGPUs > s.availableGPUs {
		return &SchedulerError{Code: "CAPACITY_EXCEEDED", Message: "Cluster lacks requested capacity"}
	}

	job.Status = StatusPending
	s.jobQueue = append(s.jobQueue, job)
	return nil
}

// Tick attempts to schedule pending jobs
func (s *JobScheduler) Tick() {
	for _, job := range s.jobQueue {
		if job.Status == StatusPending {
			if s.allocateResources(job.RequiredGPUs) {
				job.Status = StatusRunning
				fmt.Printf("[Higgsfield] Job %s Scheduled on %d GPUs at %v\n", job.JobID, job.RequiredGPUs, time.Now())
			}
		}
	}
}

func (s *JobScheduler) allocateResources(requested int) bool {
	// In production, this locks resources in Etcd or Redis
	if s.availableGPUs >= requested {
		s.availableGPUs -= requested
		return true
	}
	return false
}
