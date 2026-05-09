// moe_grpc_service.go — gRPC Service for MoE Expert Inference
// Layer: Network / RPC — MoE Inter-Service Communication
//
// gRPC service definitions and server implementation for MoE expert
// parallelism across machines. Handles token dispatch, expert
// execution, and result aggregation over the network.

package network_moe

import (
	"context"
	"fmt"
	"log"
	"math"
	"sync"
	"sync/atomic"
	"time"
)

// Token represents a single token for expert processing.
type Token struct {
	TokenID    int32     `json:"token_id"`
	Data       []float32 `json:"data"`
	ExpertID   int32     `json:"expert_id"`
	Weight     float32   `json:"weight"`
	SourceRank int32     `json:"source_rank"`
}

// ExpertOutput contains the processed output from an expert.
type ExpertOutput struct {
	TokenID  int32     `json:"token_id"`
	Data     []float32 `json:"data"`
	ExpertID int32     `json:"expert_id"`
	Weight   float32   `json:"weight"`
}

// DispatchRequest is a batch of tokens to send to experts.
type DispatchRequest struct {
	RequestID string  `json:"request_id"`
	Tokens    []Token `json:"tokens"`
	Deadline  int64   `json:"deadline_ms"`
}

// DispatchResponse is the collected expert outputs.
type DispatchResponse struct {
	RequestID string         `json:"request_id"`
	Outputs   []ExpertOutput `json:"outputs"`
	LatencyMs float64        `json:"latency_ms"`
	Status    string         `json:"status"`
}

// ExpertWorkerConfig configures a single expert worker.
type ExpertWorkerConfig struct {
	ExpertID int32
	Dim      int
	FFDim    int
	MaxBatch int
	DeviceID int
}

// ExpertWorker processes tokens for a specific expert.
type ExpertWorker struct {
	config          ExpertWorkerConfig
	tokensProcessed atomic.Int64
	avgLatencyUs    atomic.Int64
	errorCount      atomic.Int64
	mu              sync.Mutex
}

func NewExpertWorker(config ExpertWorkerConfig) *ExpertWorker {
	return &ExpertWorker{config: config}
}

// Process executes the expert computation on a batch of tokens.
func (w *ExpertWorker) Process(ctx context.Context, tokens []Token) ([]ExpertOutput, error) {
	start := time.Now()
	defer func() {
		elapsed := time.Since(start).Microseconds()
		w.tokensProcessed.Add(int64(len(tokens)))
		// EMA update
		old := w.avgLatencyUs.Load()
		newAvg := (old*95 + elapsed*5) / 100
		w.avgLatencyUs.Store(newAvg)
	}()

	select {
	case <-ctx.Done():
		w.errorCount.Add(1)
		return nil, ctx.Err()
	default:
	}

	outputs := make([]ExpertOutput, len(tokens))
	for i, tok := range tokens {
		// In production: call into GPU kernel via CGO/FFI
		outData := make([]float32, len(tok.Data))
		for j := range outData {
			outData[j] = tok.Data[j] * 0.99 // placeholder transform
		}
		outputs[i] = ExpertOutput{
			TokenID:  tok.TokenID,
			Data:     outData,
			ExpertID: w.config.ExpertID,
			Weight:   tok.Weight,
		}
	}

	return outputs, nil
}

func (w *ExpertWorker) Stats() map[string]interface{} {
	return map[string]interface{}{
		"expert_id":        w.config.ExpertID,
		"tokens_processed": w.tokensProcessed.Load(),
		"avg_latency_us":   w.avgLatencyUs.Load(),
		"error_count":      w.errorCount.Load(),
	}
}

// MoEGRPCServer manages expert workers and handles dispatch requests.
type MoEGRPCServer struct {
	workers      map[int32]*ExpertWorker
	localStart   int32
	localEnd     int32
	maxBatchSize int
	mu           sync.RWMutex
}

func NewMoEGRPCServer(startExpert, endExpert int32, dim, ffDim, maxBatch int) *MoEGRPCServer {
	workers := make(map[int32]*ExpertWorker)
	for e := startExpert; e < endExpert; e++ {
		workers[e] = NewExpertWorker(ExpertWorkerConfig{
			ExpertID: e,
			Dim:      dim,
			FFDim:    ffDim,
			MaxBatch: maxBatch,
			DeviceID: int(e - startExpert),
		})
	}
	return &MoEGRPCServer{
		workers:      workers,
		localStart:   startExpert,
		localEnd:     endExpert,
		maxBatchSize: maxBatch,
	}
}

// DispatchTokens processes a batch of tokens on local experts.
func (s *MoEGRPCServer) DispatchTokens(ctx context.Context, req *DispatchRequest) (*DispatchResponse, error) {
	start := time.Now()

	// Group tokens by expert
	grouped := make(map[int32][]Token)
	for _, tok := range req.Tokens {
		if tok.ExpertID >= s.localStart && tok.ExpertID < s.localEnd {
			grouped[tok.ExpertID] = append(grouped[tok.ExpertID], tok)
		}
	}

	// Process each expert's tokens in parallel
	type result struct {
		outputs []ExpertOutput
		err     error
	}

	results := make(chan result, len(grouped))
	var wg sync.WaitGroup

	for expertID, tokens := range grouped {
		wg.Add(1)
		go func(eid int32, toks []Token) {
			defer wg.Done()
			worker, ok := s.workers[eid]
			if !ok {
				results <- result{nil, fmt.Errorf("expert %d not found", eid)}
				return
			}
			outs, err := worker.Process(ctx, toks)
			results <- result{outs, err}
		}(expertID, tokens)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	var allOutputs []ExpertOutput
	for r := range results {
		if r.err != nil {
			return &DispatchResponse{
				RequestID: req.RequestID,
				Status:    "error: " + r.err.Error(),
				LatencyMs: float64(time.Since(start).Microseconds()) / 1000.0,
			}, nil
		}
		allOutputs = append(allOutputs, r.outputs...)
	}

	return &DispatchResponse{
		RequestID: req.RequestID,
		Outputs:   allOutputs,
		LatencyMs: float64(time.Since(start).Microseconds()) / 1000.0,
		Status:    "ok",
	}, nil
}

// GetAllStats returns stats for all local expert workers.
func (s *MoEGRPCServer) GetAllStats() []map[string]interface{} {
	s.mu.RLock()
	defer s.mu.RUnlock()
	stats := make([]map[string]interface{}, 0, len(s.workers))
	for _, w := range s.workers {
		stats = append(stats, w.Stats())
	}
	return stats
}

// HealthCheck returns the server health status.
func (s *MoEGRPCServer) HealthCheck() map[string]interface{} {
	totalProcessed := int64(0)
	totalErrors := int64(0)
	for _, w := range s.workers {
		totalProcessed += w.tokensProcessed.Load()
		totalErrors += w.errorCount.Load()
	}
	errorRate := float64(0)
	if totalProcessed > 0 {
		errorRate = float64(totalErrors) / float64(totalProcessed+totalErrors)
	}
	return map[string]interface{}{
		"status":          "healthy",
		"local_experts":   fmt.Sprintf("[%d, %d)", s.localStart, s.localEnd),
		"total_processed": totalProcessed,
		"error_rate":      math.Round(errorRate*10000) / 10000,
	}
}

// Suppress unused import warning
var _ = log.Println

