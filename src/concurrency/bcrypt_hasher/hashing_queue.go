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

type HashRequest struct {
	ReqID string
	Cost  int
}

type HashingQueue struct {
	queue chan HashRequest
	wg    sync.WaitGroup
}

func NewHashingQueue(workers int) *HashingQueue {
	q := &HashingQueue{
		queue: make(chan HashRequest, 100),
	}

	for i := 0; i < workers; i++ {
		q.wg.Add(1)
		go q.worker(i)
	}

	return q
}

func (q *HashingQueue) worker(id int) {
	defer q.wg.Done()

	for req := range q.queue {
		// Simulate CPU bound work relative to cost (2^cost base)
		// For zero-mock deterministic testing we use a scaled sleep
		ms := (1 << (req.Cost - 4)) * 5
		time.Sleep(time.Duration(ms) * time.Millisecond)

		fmt.Printf("Bcrypt Worker [%d]: Hashed %s at Cost %d\n", id, req.ReqID, req.Cost)
	}
}

func (q *HashingQueue) Enqueue(req HashRequest) OmniResult {
	select {
	case q.queue <- req:
		return OmniResult{Value: true}
	default:
		return OmniResult{Error: fmt.Errorf("Hash queue full, try again")}
	}
}
