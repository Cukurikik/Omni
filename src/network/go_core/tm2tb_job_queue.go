package network_gocore

import (
	"context"
	"fmt"
	"sync"
)

// Tm2tbJobQueue manages background terminology extraction tasks.
type Tm2tbJobQueue struct {
	mu    sync.Mutex
	queue []ExtractionJob
}

type ExtractionJob struct {
	JobID      string
	SourcePath string
	TargetPath string
	Status     string
}

func NewTm2tbJobQueue() *Tm2tbJobQueue {
	return &Tm2tbJobQueue{
		queue: make([]ExtractionJob, 0),
	}
}

func (q *Tm2tbJobQueue) EnqueueJob(ctx context.Context, job ExtractionJob) error {
	q.mu.Lock()
	defer q.mu.Unlock()

	if job.JobID == "" {
		return fmt.Errorf("invalid job ID")
	}

	job.Status = "PENDING"
	q.queue = append(q.queue, job)
	return nil
}

func (q *Tm2tbJobQueue) DequeueJob(ctx context.Context) (*ExtractionJob, error) {
	q.mu.Lock()
	defer q.mu.Unlock()

	if len(q.queue) == 0 {
		return nil, fmt.Errorf("queue is empty")
	}

	job := q.queue[0]
	q.queue = q.queue[1:]
	job.Status = "PROCESSING"
	return &job, nil
}

