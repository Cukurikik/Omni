package concurrency

import (
	"time"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type ParticlePool struct {
	numParticles int
	weights      []float64
	mu           sync.RWMutex
}

func NewParticlePool(num int) *ParticlePool {
	return &ParticlePool{
		numParticles: num,
		weights:      make([]float64, num),
	}
}

func (p *ParticlePool) ParallelUpdate() OmniResult {
	p.mu.Lock()
	defer p.mu.Unlock()

	var wg sync.WaitGroup
	chunkSize := p.numParticles / 4
	if chunkSize == 0 {
		chunkSize = 1
	}

	for i := 0; i < p.numParticles; i += chunkSize {
		end := i + chunkSize
		if end > p.numParticles {
			end = p.numParticles
		}

		wg.Add(1)
		go func(start, end int) {
			defer wg.Done()
			for j := start; j < end; j++ {
				// Simulate intensive probabilistic update
				time.Sleep(1 * time.Microsecond)
				p.weights[j] = 1.0 // Reset weight
			}
		}(i, end)
	}

	wg.Wait()
	return OmniResult{Value: true}
}
