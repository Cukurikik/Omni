package sqlflow

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"time"
)

// OMNI Concurrency Layer: SQLFlow Job Submitter (Go)
// Manages ML pipeline submission parsed from SQL to execution backends.

type JobStatus string

const (
	StatusPending JobStatus = "PENDING"
	StatusRunning JobStatus = "RUNNING"
	StatusDone    JobStatus = "DONE"
	StatusFailed  JobStatus = "FAILED"
)

type MLJob struct {
	JobID      string
	SQL        string
	ModelType  string
	DataSource string
	Status     JobStatus
	CreatedAt  time.Time
}

type JobSubmitter struct {
	mu   sync.RWMutex
	jobs map[string]*MLJob
}

func NewJobSubmitter() *JobSubmitter {
	return &JobSubmitter{
		jobs: make(map[string]*MLJob),
	}
}

func (s *JobSubmitter) SubmitJob(ctx context.Context, sql, modelType, dataSource string) (*MLJob, error) {
	if sql == "" || modelType == "" {
		return nil, errors.New("SQL and ModelType cannot be empty")
	}

	jobID := fmt.Sprintf("job-%d", time.Now().UnixNano())
	job := &MLJob{
		JobID:      jobID,
		SQL:        sql,
		ModelType:  modelType,
		DataSource: dataSource,
		Status:     StatusPending,
		CreatedAt:  time.Now(),
	}

	s.mu.Lock()
	s.jobs[jobID] = job
	s.mu.Unlock()

	// Asynchronous execution invocation
	go s.executeJob(job)

	return job, nil
}

func (s *JobSubmitter) executeJob(job *MLJob) {
	s.mu.Lock()
	job.Status = StatusRunning
	s.mu.Unlock()

	// Strictly monadic execution pipeline
	err := s.runTrainLoop(job)

	s.mu.Lock()
	defer s.mu.Unlock()
	if err != nil {
		job.Status = StatusFailed
	} else {
		job.Status = StatusDone
	}
}

func (s *JobSubmitter) runTrainLoop(job *MLJob) error {
	// Emulate database load and train execution natively
	time.Sleep(200 * time.Millisecond) // Native OMNI delay for external FFI call
	return nil
}

func (s *JobSubmitter) GetStatus(jobID string) (JobStatus, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	job, exists := s.jobs[jobID]
	if !exists {
		return "", errors.New("job not found")
	}
	return job.Status, nil
}
