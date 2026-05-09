// omni_batch_scheduler.go — Dynamic Request Batching Engine
// Inspired by: OMNI inference server batching requirements
// Layer: Network / Go
//
// Adaptive request batching with timeout-based flushing,
// priority queues, and maximum batch size enforcement.

package scheduler

import (
	"context"
	"sync"
	"sync/atomic"
	"time"
)

type Priority int

const (
	PriorityLow    Priority = 0
	PriorityNormal Priority = 1
	PriorityHigh   Priority = 2
)

type InferenceRequest struct {
	ID        string
	Input     []float32
	InputLen  int
	Priority  Priority
	CreatedAt time.Time
	Deadline  time.Time
	ResultCh  chan InferenceResult
}

type InferenceResult struct {
	RequestID string
	Output    []float32
	LatencyMs float64
	Error     error
}

type BatchConfig struct {
	MaxBatchSize    int
	MaxWaitMs       int
	MinBatchSize    int
	PaddingStrategy string // "max_len" or "bucket"
	BucketSizes     []int
}

type Batch struct {
	Requests  []*InferenceRequest
	MaxSeqLen int
	CreatedAt time.Time
	BatchID   uint64
}

type BatchProcessor interface {
	ProcessBatch(ctx context.Context, batch *Batch) ([][]float32, error)
}

type OmniBatchScheduler struct {
	config    BatchConfig
	processor BatchProcessor

	mu          sync.Mutex
	highQueue   []*InferenceRequest
	normalQueue []*InferenceRequest
	lowQueue    []*InferenceRequest

	batchCounter   atomic.Uint64
	totalProcessed atomic.Int64
	totalBatches   atomic.Int64

	running atomic.Bool
	stopCh  chan struct{}
}

func NewBatchScheduler(config BatchConfig, processor BatchProcessor) *OmniBatchScheduler {
	if config.MaxBatchSize <= 0 {
		config.MaxBatchSize = 32
	}
	if config.MaxWaitMs <= 0 {
		config.MaxWaitMs = 50
	}
	if config.MinBatchSize <= 0 {
		config.MinBatchSize = 1
	}
	if len(config.BucketSizes) == 0 {
		config.BucketSizes = []int{128, 256, 512, 1024, 2048}
	}

	return &OmniBatchScheduler{
		config:      config,
		processor:   processor,
		highQueue:   make([]*InferenceRequest, 0, 64),
		normalQueue: make([]*InferenceRequest, 0, 64),
		lowQueue:    make([]*InferenceRequest, 0, 64),
		stopCh:      make(chan struct{}),
	}
}

func (s *OmniBatchScheduler) Submit(req *InferenceRequest) {
	if req.ResultCh == nil {
		req.ResultCh = make(chan InferenceResult, 1)
	}
	if req.CreatedAt.IsZero() {
		req.CreatedAt = time.Now()
	}

	s.mu.Lock()
	switch req.Priority {
	case PriorityHigh:
		s.highQueue = append(s.highQueue, req)
	case PriorityNormal:
		s.normalQueue = append(s.normalQueue, req)
	default:
		s.lowQueue = append(s.lowQueue, req)
	}
	s.mu.Unlock()
}

func (s *OmniBatchScheduler) Start(ctx context.Context) {
	s.running.Store(true)

	go func() {
		ticker := time.NewTicker(time.Duration(s.config.MaxWaitMs) * time.Millisecond)
		defer ticker.Stop()

		for {
			select {
			case <-ctx.Done():
				s.running.Store(false)
				return
			case <-s.stopCh:
				s.running.Store(false)
				return
			case <-ticker.C:
				s.tryFlush(ctx)
			}
		}
	}()
}

func (s *OmniBatchScheduler) Stop() {
	close(s.stopCh)
}

func (s *OmniBatchScheduler) tryFlush(ctx context.Context) {
	s.mu.Lock()
	totalPending := len(s.highQueue) + len(s.normalQueue) + len(s.lowQueue)

	if totalPending < s.config.MinBatchSize {
		s.mu.Unlock()
		return
	}

	// Build batch: priority order
	batch := &Batch{
		Requests:  make([]*InferenceRequest, 0, s.config.MaxBatchSize),
		CreatedAt: time.Now(),
		BatchID:   s.batchCounter.Add(1),
	}

	remaining := s.config.MaxBatchSize

	// High priority first
	take := min(remaining, len(s.highQueue))
	batch.Requests = append(batch.Requests, s.highQueue[:take]...)
	s.highQueue = s.highQueue[take:]
	remaining -= take

	// Normal priority
	take = min(remaining, len(s.normalQueue))
	batch.Requests = append(batch.Requests, s.normalQueue[:take]...)
	s.normalQueue = s.normalQueue[take:]
	remaining -= take

	// Low priority
	take = min(remaining, len(s.lowQueue))
	batch.Requests = append(batch.Requests, s.lowQueue[:take]...)
	s.lowQueue = s.lowQueue[take:]

	// Compute max sequence length
	for _, req := range batch.Requests {
		if req.InputLen > batch.MaxSeqLen {
			batch.MaxSeqLen = req.InputLen
		}
	}

	// Apply bucketing
	batch.MaxSeqLen = s.findBucket(batch.MaxSeqLen)

	s.mu.Unlock()

	if len(batch.Requests) == 0 {
		return
	}

	// Process batch asynchronously
	go s.processBatch(ctx, batch)
}

func (s *OmniBatchScheduler) processBatch(ctx context.Context, batch *Batch) {
	startTime := time.Now()

	outputs, err := s.processor.ProcessBatch(ctx, batch)

	elapsed := time.Since(startTime).Seconds() * 1000

	s.totalBatches.Add(1)
	s.totalProcessed.Add(int64(len(batch.Requests)))

	for i, req := range batch.Requests {
		result := InferenceResult{
			RequestID: req.ID,
			LatencyMs: elapsed,
			Error:     err,
		}
		if err == nil && i < len(outputs) {
			result.Output = outputs[i]
		}
		select {
		case req.ResultCh <- result:
		default:
			// Channel full, skip
		}
	}
}

func (s *OmniBatchScheduler) findBucket(seqLen int) int {
	for _, bucket := range s.config.BucketSizes {
		if seqLen <= bucket {
			return bucket
		}
	}
	return seqLen
}

func (s *OmniBatchScheduler) PendingCount() int {
	s.mu.Lock()
	defer s.mu.Unlock()
	return len(s.highQueue) + len(s.normalQueue) + len(s.lowQueue)
}

func (s *OmniBatchScheduler) Stats() map[string]int64 {
	return map[string]int64{
		"total_processed": s.totalProcessed.Load(),
		"total_batches":   s.totalBatches.Load(),
		"pending":         int64(s.PendingCount()),
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
