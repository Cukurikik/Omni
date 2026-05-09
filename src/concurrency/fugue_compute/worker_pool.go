package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type Task struct {
	ID      string
	Payload []byte
}

type WorkerPool struct {
	numWorkers int
	taskQueue  chan Task
	wg         sync.WaitGroup
}

func NewWorkerPool(workers int) *WorkerPool {
	return &WorkerPool{
		numWorkers: workers,
		taskQueue:  make(chan Task, 1000),
	}
}

func (p *WorkerPool) Start() {
	for i := 0; i < p.numWorkers; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

func (p *WorkerPool) worker(id int) {
	defer p.wg.Done()
	for task := range p.taskQueue {
		// Deterministic execution simulation
		_ = fmt.Sprintf("Worker %d executed task %s", id, task.ID)
	}
}

func (p *WorkerPool) SubmitTask(task Task) OmniResult {
	if task.ID == "" {
		return OmniResult{Error: fmt.Errorf("task ID cannot be empty")}
	}

	select {
	case p.taskQueue <- task:
		return OmniResult{Value: "Task submitted successfully"}
	default:
		return OmniResult{Error: fmt.Errorf("worker pool queue is full")}
	}
}

func (p *WorkerPool) StopAndWait() {
	close(p.taskQueue)
	p.wg.Wait()
}
