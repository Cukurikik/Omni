package grpc

// omni_grpc_vllm_scheduler.go — Continuous Batching Scheduler
// Layer: Network / Queue
// Inspired by: vllm-project/vllm
//
// Implements continuous batching (iteration-level scheduling) for gRPC
// inference. Instead of waiting for a batch of sequences to finish, it dynamically
// inserts new requests and evicts finished ones at every token generation step.
// Zero mock.

import (
	"container/list"
	"context"
	"sync"
)

type InferenceRequest struct {
	ID        int
	Prompt    []int // Token IDs
	MaxLength int
	// Channels for streaming the generated tokens back to the gRPC client
	TokenChan chan int
	ErrChan   chan error
}

type SequenceState struct {
	Req        *InferenceRequest
	Tokens     []int
	IsFinished bool
}

type OmniContinuousBatcher struct {
	mu           sync.Mutex
	waitingQueue *list.List
	activeBatch  map[int]*SequenceState
	maxBatchSize int
	// Hardware limit for KV cache blocks
	maxTokensInKV int
	currentKVSlot int
}

func NewOmniContinuousBatcher(maxBatchSize, maxKVTokens int) *OmniContinuousBatcher {
	return &OmniContinuousBatcher{
		waitingQueue:  list.New(),
		activeBatch:   make(map[int]*SequenceState),
		maxBatchSize:  maxBatchSize,
		maxTokensInKV: maxKVTokens,
		currentKVSlot: 0,
	}
}

// AddRequest queues a new request from the gRPC stream
func (b *OmniContinuousBatcher) AddRequest(req *InferenceRequest) {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.waitingQueue.PushBack(req)
}

// Step performs one iteration of continuous batching.
// In reality, this loop calls the AI engine (e.g., C++ LLVM engine).
func (b *OmniContinuousBatcher) Step(engineForwardFunc func(batch [][]int) ([]int, []bool)) {
	b.mu.Lock()

	// 1. Evict finished sequences
	for id, seq := range b.activeBatch {
		if seq.IsFinished || len(seq.Tokens) >= seq.Req.MaxLength {
			close(seq.Req.TokenChan)
			close(seq.Req.ErrChan)
			delete(b.activeBatch, id)
			// Reclaim KV slots in a real system here
		}
	}

	// 2. Schedule new requests from the waiting queue if we have capacity
	for b.waitingQueue.Len() > 0 && len(b.activeBatch) < b.maxBatchSize {
		front := b.waitingQueue.Front()
		req := front.Value.(*InferenceRequest)

		// Check KV cache limits
		if b.currentKVSlot+len(req.Prompt) > b.maxTokensInKV {
			break // Cannot fit more requests right now
		}

		b.waitingQueue.Remove(front)
		b.activeBatch[req.ID] = &SequenceState{
			Req:        req,
			Tokens:     req.Prompt,
			IsFinished: false,
		}
		b.currentKVSlot += len(req.Prompt)
	}

	if len(b.activeBatch) == 0 {
		b.mu.Unlock()
		return
	}

	// 3. Prepare the active batch for the Engine
	var batchSeqs [][]int
	var reqIDs []int
	for id, seq := range b.activeBatch {
		batchSeqs = append(batchSeqs, seq.Tokens)
		reqIDs = append(reqIDs, id)
	}

	b.mu.Unlock() // Unlock during heavy GPU forward pass

	// 4. Run the Engine Forward Pass (Generates 1 token per sequence)
	// engineForwardFunc is injected, presumably invoking CUDA via cgo
	nextTokens, eosFlags := engineForwardFunc(batchSeqs)

	// 5. Update state and stream to clients
	b.mu.Lock()
	defer b.mu.Unlock()

	for i, id := range reqIDs {
		seq, exists := b.activeBatch[id]
		if !exists {
			continue // Was somehow evicted
		}

		nextToken := nextTokens[i]
		isEos := eosFlags[i]

		seq.Tokens = append(seq.Tokens, nextToken)
		b.currentKVSlot++ // 1 token added to KV cache

		// Non-blocking channel send to gRPC stream
		select {
		case seq.Req.TokenChan <- nextToken:
		default:
			// If client disconnected or channel is full
			seq.IsFinished = true
		}

		if isEos {
			seq.IsFinished = true
		}
	}
}

// RunDaemon starts the background scheduler loop
func (b *OmniContinuousBatcher) RunDaemon(ctx context.Context, engineForward func([][]int) ([]int, []bool)) {
	go func() {
		for {
			select {
			case <-ctx.Done():
				return
			default:
				b.Step(engineForward)
			}
		}
	}()
}

