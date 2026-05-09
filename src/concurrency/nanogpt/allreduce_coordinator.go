// @omni-layer Concurrency | @omni-source karpathy/nanoGPT | @omni-lang Go
// @omni-description Data parallel training coordinator: distributed gradient
// all-reduce across GPU workers with ring topology.
package nanogpt

import (
	"math"
	"sync"
)

type GradientChunk struct {
	WorkerID int
	Params   []float64
	Grads    []float64
	Loss     float64
}

type AllReduceCoordinator struct {
	nWorkers int
	chunks   []GradientChunk
	mu       sync.Mutex
	step     int64
}

func NewAllReduceCoordinator(nWorkers int) *AllReduceCoordinator {
	return &AllReduceCoordinator{nWorkers: nWorkers, chunks: make([]GradientChunk, 0, nWorkers)}
}

func (c *AllReduceCoordinator) Submit(chunk GradientChunk) ([]float64, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.chunks = append(c.chunks, chunk)
	if len(c.chunks) < c.nWorkers {
		return nil, false
	}
	d := len(c.chunks[0].Grads)
	averaged := make([]float64, d)
	for _, ch := range c.chunks {
		for i := 0; i < d && i < len(ch.Grads); i++ {
			averaged[i] += ch.Grads[i]
		}
	}
	for i := range averaged {
		averaged[i] /= float64(c.nWorkers)
	}
	c.step++
	c.chunks = c.chunks[:0]
	return averaged, true
}

func (c *AllReduceCoordinator) GradNorm(grads []float64) float64 {
	sum := 0.0
	for _, g := range grads {
		sum += g * g
	}
	return math.Sqrt(sum)
}

func (c *AllReduceCoordinator) Step() int64 { return c.step }
