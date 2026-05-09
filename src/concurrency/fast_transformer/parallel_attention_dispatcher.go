// @omni-layer Concurrency | @omni-source lucidrains/fast-transformer-pytorch
// @omni-description Parallel attention dispatcher in Go: distributes O(n) fast
// attention across multiple goroutines for sequence parallelism.
// @omni-lang Go | @omni-batch 16 | @omni-semester 16
package fast_transformer

import (
	"math"
	"sync"
)

type AttentionChunk struct {
	QueryStart int
	QueryEnd   int
	Output     [][]float64
}

type ParallelAttentionDispatcher struct {
	dModel   int
	nWorkers int
}

func NewParallelAttentionDispatcher(dModel, nWorkers int) *ParallelAttentionDispatcher {
	return &ParallelAttentionDispatcher{dModel: dModel, nWorkers: nWorkers}
}

func (d *ParallelAttentionDispatcher) globalAggregate(queries [][]float64) []float64 {
	n := len(queries)
	if n == 0 {
		return nil
	}
	dim := len(queries[0])
	logits := make([]float64, n)
	for i, q := range queries {
		s := 0.0
		for j := 0; j < dim && j < 16; j++ {
			s += q[j] * 0.01
		}
		logits[i] = s
	}
	maxL := logits[0]
	for _, l := range logits {
		if l > maxL {
			maxL = l
		}
	}
	expSum := 0.0
	for _, l := range logits {
		expSum += math.Exp(l - maxL)
	}
	global := make([]float64, dim)
	for i, q := range queries {
		w := math.Exp(logits[i]-maxL) / (expSum + 1e-8)
		for j := range global {
			global[j] += w * q[j]
		}
	}
	return global
}

func (d *ParallelAttentionDispatcher) DispatchParallel(queries, keys, values [][]float64) [][]float64 {
	n := len(queries)
	if n == 0 {
		return nil
	}
	globalQ := d.globalAggregate(queries)
	globalK := d.globalAggregate(keys)
	output := make([][]float64, n)
	chunkSize := (n + d.nWorkers - 1) / d.nWorkers
	var wg sync.WaitGroup
	for w := 0; w < d.nWorkers; w++ {
		start := w * chunkSize
		end := start + chunkSize
		if end > n {
			end = n
		}
		if start >= n {
			break
		}
		wg.Add(1)
		go func(s, e int) {
			defer wg.Done()
			dim := len(queries[0])
			for i := s; i < e; i++ {
				out := make([]float64, dim)
				for j := 0; j < dim; j++ {
					out[j] = values[i][j]*globalK[j] + queries[i][j]
				}
				output[i] = out
			}
		}(start, end)
	}
	wg.Wait()
	_ = globalQ
	return output
}
