package concurrency

import (
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type GradientAccumulator struct {
	gradients map[string][]float32
	mu        sync.Mutex
	cond      *sync.Cond
	pending   int
	expected  int
}

func NewGradientAccumulator(expectedWorkers int) *GradientAccumulator {
	g := &GradientAccumulator{
		gradients: make(map[string][]float32),
		expected:  expectedWorkers,
		pending:   expectedWorkers,
	}
	g.cond = sync.NewCond(&g.mu)
	return g
}

func (g *GradientAccumulator) SubmitLocalGradients(workerID int, localGrads map[string][]float32) OmniResult {
	g.mu.Lock()
	defer g.mu.Unlock()

	// Deterministic accumulation (summation)
	for paramName, gradArray := range localGrads {
		if _, exists := g.gradients[paramName]; !exists {
			g.gradients[paramName] = make([]float32, len(gradArray))
		}
		
		for i, v := range gradArray {
			g.gradients[paramName][i] += v
		}
	}

	g.pending--
	if g.pending == 0 {
		g.cond.Broadcast() // All workers done
	}

	return OmniResult{Value: true}
}

func (g *GradientAccumulator) WaitForGlobalGradients() OmniResult {
	g.mu.Lock()
	defer g.mu.Unlock()

	for g.pending > 0 {
		g.cond.Wait()
	}

	// Reset for next iteration (Backprop cycle)
	g.pending = g.expected
	
	// Copy to return
	globalCopy := make(map[string][]float32)
	for k, v := range g.gradients {
		globalCopy[k] = v
	}
	
	// Zero out gradients deterministically for next step
	for k := range g.gradients {
		for i := range g.gradients[k] {
			g.gradients[k][i] = 0.0
		}
	}

	return OmniResult{Value: globalCopy}
}
