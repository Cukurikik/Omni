package concurrency

import (
	"time"
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SignRequest struct {
	PayloadHash string
}

type WorkerQueue struct {
	queue chan SignRequest
	wg    sync.WaitGroup
}

func NewWorkerQueue(workers int) *WorkerQueue {
	q := &WorkerQueue{
		queue: make(chan SignRequest, 100),
	}

	for i := 0; i < workers; i++ {
		q.wg.Add(1)
		go q.worker(i)
	}

	return q
}

func (q *WorkerQueue) worker(id int) {
	defer q.wg.Done()
	
	for req := range q.queue {
		// Simulate heavy RSA signing latency (PKCS#1 v1.5 / PSS)
		time.Sleep(10 * time.Millisecond)
		if len(req.PayloadHash) > 0 {
			// fmt.Printf("RSA Worker [%d]: Signed payload %s\n", id, req.PayloadHash)
		}
	}
}

func (q *WorkerQueue) Submit(req SignRequest) OmniResult {
	select {
	case q.queue <- req:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Signer queue saturated (CPU bound)")}
	}
}
