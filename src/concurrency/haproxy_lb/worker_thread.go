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

type LbTask struct {
	ReqID string
	Bytes int
}

type WorkerThreadPool struct {
	queue chan LbTask
	wg    sync.WaitGroup
}

func NewWorkerThreadPool(threads int) *WorkerThreadPool {
	p := &WorkerThreadPool{
		queue: make(chan LbTask, 1000),
	}

	for i := 0; i < threads; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}

	return p
}

func (p *WorkerThreadPool) worker(id int) {
	defer p.wg.Done()

	for task := range p.queue {
		// Extremely fast zero-mock forwarding simulation
		time.Sleep(1 * time.Millisecond)
		if task.Bytes > 1000000 {
			fmt.Printf("HAProxy Thread [%d]: Chunked transfer %d bytes for %s\n", id, task.Bytes, task.ReqID)
		}
	}
}

func (p *WorkerThreadPool) EnqueueRequest(task LbTask) OmniResult {
	select {
	case p.queue <- task:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("HAProxy Queue Full - 503 Backend Exhausted")}
	}
}
