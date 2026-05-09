// @omni-layer Concurrency | @omni-lang Go | @omni-batch 18 | @omni-semester 16
// @omni-description Go transformer batch scheduler: concurrent batch formation,
// dynamic batching, and priority-based request scheduling.
package batchscheduler

import (
	"container/heap"
	"fmt"
	"sync"
	"time"
)

type Priority int

const (
	Low    Priority = 0
	Normal Priority = 1
	High   Priority = 2
	Urgent Priority = 3
)

type BatchRequest struct {
	ID        string
	ModelID   string
	Tokens    []int32
	Priority  Priority
	CreatedAt time.Time
	Deadline  time.Time
}

type priorityQueue []*BatchRequest

func (pq priorityQueue) Len() int            { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool  { return pq[i].Priority > pq[j].Priority }
func (pq priorityQueue) Swap(i, j int)       { pq[i], pq[j] = pq[j], pq[i] }
func (pq *priorityQueue) Push(x interface{}) { *pq = append(*pq, x.(*BatchRequest)) }
func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[:n-1]
	return item
}

type Batch struct {
	ID       string
	ModelID  string
	Requests []*BatchRequest
	Size     int
	Tokens   int
}

type BatchScheduler struct {
	mu             sync.Mutex
	queues         map[string]*priorityQueue
	maxBatchSize   int
	maxBatchTokens int
	batchTimeout   time.Duration
	batchChan      chan *Batch
	stopChan       chan struct{}
	stats          struct {
		batchesFormed  int64
		requestsServed int64
	}
}

func NewBatchScheduler(maxSize, maxTokens int, timeout time.Duration) *BatchScheduler {
	return &BatchScheduler{
		queues:         make(map[string]*priorityQueue),
		maxBatchSize:   maxSize,
		maxBatchTokens: maxTokens,
		batchTimeout:   timeout,
		batchChan:      make(chan *Batch, 100),
		stopChan:       make(chan struct{}),
	}
}

func (bs *BatchScheduler) Submit(req *BatchRequest) {
	bs.mu.Lock()
	defer bs.mu.Unlock()
	if _, ok := bs.queues[req.ModelID]; !ok {
		pq := &priorityQueue{}
		heap.Init(pq)
		bs.queues[req.ModelID] = pq
	}
	heap.Push(bs.queues[req.ModelID], req)
}

func (bs *BatchScheduler) Start() {
	go bs.schedulerLoop()
}

func (bs *BatchScheduler) Stop() {
	close(bs.stopChan)
}

func (bs *BatchScheduler) Batches() <-chan *Batch {
	return bs.batchChan
}

func (bs *BatchScheduler) schedulerLoop() {
	ticker := time.NewTicker(bs.batchTimeout / 2)
	defer ticker.Stop()
	for {
		select {
		case <-bs.stopChan:
			return
		case <-ticker.C:
			bs.formBatches()
		}
	}
}

func (bs *BatchScheduler) formBatches() {
	bs.mu.Lock()
	defer bs.mu.Unlock()
	for modelID, pq := range bs.queues {
		if pq.Len() == 0 {
			continue
		}
		batch := &Batch{
			ID:      fmt.Sprintf("batch-%s-%d", modelID, time.Now().UnixNano()),
			ModelID: modelID,
		}
		totalTokens := 0
		for pq.Len() > 0 && batch.Size < bs.maxBatchSize {
			req := heap.Pop(pq).(*BatchRequest)
			reqTokens := len(req.Tokens)
			if totalTokens+reqTokens > bs.maxBatchTokens && batch.Size > 0 {
				heap.Push(pq, req)
				break
			}
			batch.Requests = append(batch.Requests, req)
			batch.Size++
			totalTokens += reqTokens
		}
		batch.Tokens = totalTokens
		if batch.Size > 0 {
			bs.stats.batchesFormed++
			bs.stats.requestsServed += int64(batch.Size)
			select {
			case bs.batchChan <- batch:
			default:
			}
		}
	}
}

func (bs *BatchScheduler) Stats() map[string]int64 {
	bs.mu.Lock()
	defer bs.mu.Unlock()
	return map[string]int64{
		"batches_formed":  bs.stats.batchesFormed,
		"requests_served": bs.stats.requestsServed,
	}
}
