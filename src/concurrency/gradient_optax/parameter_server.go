package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type GradientUpdate struct {
	WorkerID int
	Gradients []float64
}

type ParameterServer struct {
	params []float64
	mu     sync.RWMutex
}

func NewParameterServer(size int) *ParameterServer {
	return &ParameterServer{
		params: make([]float64, size),
	}
}

func (p *ParameterServer) ApplyGradients(update GradientUpdate) OmniResult {
	if len(update.Gradients) == 0 {
		return OmniResult{Error: fmt.Errorf("empty gradients from worker %d", update.WorkerID)}
	}

	p.mu.Lock()
	defer p.mu.Unlock()

	if len(update.Gradients) != len(p.params) {
		return OmniResult{Error: fmt.Errorf("gradient size mismatch")}
	}

	// Deterministic parameter update (simple SGD step for param server aggregation)
	learningRate := 0.01
	for i := range p.params {
		p.params[i] -= learningRate * update.Gradients[i]
	}

	return OmniResult{Value: fmt.Sprintf("Aggregated gradients from Worker %d", update.WorkerID)}
}

func (p *ParameterServer) GetParams() []float64 {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	// Return a copy to ensure thread safety
	paramsCopy := make([]float64, len(p.params))
	copy(paramsCopy, p.params)
	return paramsCopy
}
