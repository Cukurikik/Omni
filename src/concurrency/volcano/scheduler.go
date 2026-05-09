package volcano

import (
	"context"
	"fmt"
	"time"
)

type Node struct {
	ID            string
	AvailCPU      int
	AvailMemoryMB int
}

type Scheduler struct {
	Queue *VolcanoQueue
	Nodes []*Node
}

// OMNI Engine: Core bin-packing scheduler loop for Kubernetes batch jobs
func (s *Scheduler) Run(ctx context.Context) {
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			s.scheduleNext()
		}
	}
}

func (s *Scheduler) scheduleNext() {
	job := s.Queue.Dequeue()
	if job == nil {
		return
	}

	for _, node := range s.Nodes {
		if node.AvailCPU >= job.CPUCores && node.AvailMemoryMB >= job.MemoryMB {
			node.AvailCPU -= job.CPUCores
			node.AvailMemoryMB -= job.MemoryMB
			fmt.Printf("Volcano: Scheduled Job %s onto Node %s\n", job.ID, node.ID)
			return
		}
	}

	// Insufficient resources, re-queue
	s.Queue.Enqueue(job)
}
