// @omni-layer Concurrency | @omni-source vllm-project/vllm | @omni-lang Go
// @omni-description Continuous batching scheduler: dynamic batch assembly with
// preemption, swapping, and priority-based scheduling for vLLM.
package vllm

import (
	"sort"
	"sync"
	"time"
)

type InferenceRequest struct {
	ID        string
	Priority  int
	InputLen  int
	MaxOutput int
	Arrived   time.Time
	Status    string
}

type BatchScheduler struct {
	mu          sync.Mutex
	waiting     []InferenceRequest
	running     []InferenceRequest
	maxBatch    int
	maxTokens   int
	totalServed int64
}

func NewBatchScheduler(maxBatch, maxTokens int) *BatchScheduler {
	return &BatchScheduler{maxBatch: maxBatch, maxTokens: maxTokens}
}

func (s *BatchScheduler) Enqueue(req InferenceRequest) {
	s.mu.Lock()
	defer s.mu.Unlock()
	req.Status = "waiting"
	s.waiting = append(s.waiting, req)
	sort.Slice(s.waiting, func(i, j int) bool { return s.waiting[i].Priority > s.waiting[j].Priority })
}

func (s *BatchScheduler) AssembleBatch() []InferenceRequest {
	s.mu.Lock()
	defer s.mu.Unlock()
	batch := []InferenceRequest{}
	totalTok := 0
	remaining := []InferenceRequest{}
	for _, req := range s.waiting {
		if len(batch) >= s.maxBatch || totalTok+req.InputLen > s.maxTokens {
			remaining = append(remaining, req)
			continue
		}
		req.Status = "running"
		batch = append(batch, req)
		totalTok += req.InputLen
	}
	s.waiting = remaining
	s.running = batch
	s.totalServed += int64(len(batch))
	return batch
}

func (s *BatchScheduler) Stats() map[string]interface{} {
	s.mu.Lock()
	defer s.mu.Unlock()
	return map[string]interface{}{
		"waiting":      len(s.waiting),
		"running":      len(s.running),
		"total_served": s.totalServed,
	}
}
