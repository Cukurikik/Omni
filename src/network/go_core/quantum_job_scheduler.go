package network_gocore

import (
	"context"
	"fmt"
	"sync"
)

// QuantumJobScheduler queues quantum circuits for hardware backends or simulators.
type QuantumJobScheduler struct {
	mu    sync.Mutex
	Queue []QuantumJob
}

type QuantumJob struct {
	JobID    string
	Qubits   int
	Circuit  []string
	Priority int
}

func NewQuantumJobScheduler() *QuantumJobScheduler {
	return &QuantumJobScheduler{
		Queue: make([]QuantumJob, 0),
	}
}

func (s *QuantumJobScheduler) SubmitJob(ctx context.Context, job QuantumJob) error {
	if job.JobID == "" || job.Qubits <= 0 {
		return fmt.Errorf("invalid quantum job parameters")
	}

	s.mu.Lock()
	defer s.mu.Unlock()
	s.Queue = append(s.Queue, job)
	return nil
}

func (s *QuantumJobScheduler) ProcessNext(ctx context.Context) (*QuantumJob, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	if len(s.Queue) == 0 {
		return nil, fmt.Errorf("queue empty")
	}

	// Simple FIFO extraction
	job := s.Queue[0]
	s.Queue = s.Queue[1:]
	return &job, nil
}

