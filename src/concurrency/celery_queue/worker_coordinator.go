package concurrency

import (
	"fmt"
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type CeleryTask struct {
	TaskID  string
	QueueID string
	Payload string
}

type WorkerCoordinator struct {
	workerPools map[string]chan CeleryTask
	wg          sync.WaitGroup
	mu          sync.RWMutex
}

func NewWorkerCoordinator(queues []string, workersPerQueue int) *WorkerCoordinator {
	c := &WorkerCoordinator{
		workerPools: make(map[string]chan CeleryTask),
	}

	for _, q := range queues {
		c.workerPools[q] = make(chan CeleryTask, 100)
		for i := 0; i < workersPerQueue; i++ {
			c.wg.Add(1)
			go c.worker(q, i)
		}
	}

	return c
}

func (c *WorkerCoordinator) worker(queueID string, workerID int) {
	defer c.wg.Done()

	ch := c.workerPools[queueID]
	for task := range ch {
		// Deterministic task execution simulation
		time.Sleep(20 * time.Millisecond)
		fmt.Printf("Celery Worker [%s-%d]: Completed Task %s\n", queueID, workerID, task.TaskID)
	}
}

func (c *WorkerCoordinator) Dispatch(task CeleryTask) OmniResult {
	c.mu.RLock()
	defer c.mu.RUnlock()

	if ch, exists := c.workerPools[task.QueueID]; exists {
		select {
		case ch <- task:
			return OmniResult{Value: true}
		default:
			return OmniResult{Error: fmt.Errorf("Queue %s saturated", task.QueueID)}
		}
	}

	return OmniResult{Error: fmt.Errorf("Unknown queue: %s", task.QueueID)}
}
