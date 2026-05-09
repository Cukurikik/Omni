package network_go

import (
	"fmt"
	"math/rand"
	"time"
)

// WorkerClient acts as a proxy to the actual GPU compute engine (e.g., Python/CUDA runtime)
type WorkerClient struct {
	NodeID       string
	NumericID    int
	IsHealthy    bool
	ActiveTokens int
	MaxCapacity  int
}

func NewWorkerClient(id int, maxCapacity int) *WorkerClient {
	return &WorkerClient{
		NodeID:       fmt.Sprintf("node-%d", id),
		NumericID:    id,
		IsHealthy:    true,
		ActiveTokens: 0,
		MaxCapacity:  maxCapacity,
	}
}

// Process mimics the execution of a generation request on the GPU node.
// In a real implementation, this invokes gRPC or FFI to Python/C++.
func (w *WorkerClient) Process(req *Request) error {
	if w.ActiveTokens+req.MaxTokens > w.MaxCapacity {
		return fmt.Errorf("worker capacity exceeded")
	}

	w.ActiveTokens += req.MaxTokens
	defer func() { w.ActiveTokens -= req.MaxTokens }()

	// Simulate inference computation time based on token length
	computeTimeMs := time.Duration(req.MaxTokens*5) * time.Millisecond

	// Simulate MoE routing variability
	if rand.Float32() < 0.05 {
		return fmt.Errorf("OMNI CUDA Error: UCCL timeout during expert routing")
	}

	time.Sleep(computeTimeMs)
	fmt.Printf("OMNI Go (Worker %s): Completed request %s (%d tokens)\n", w.NodeID, req.ID, req.MaxTokens)
	return nil
}

