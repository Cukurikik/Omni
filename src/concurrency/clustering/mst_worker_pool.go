package clustering

import (
	"errors"
	"sort"
	"sync"
)

type Edge struct {
	U      int
	V      int
	Weight float64
}

type OmniResult struct {
	Data  []Edge
	Error error
}

type MSTWorkerPool struct {
	workers int
}

func NewMSTWorkerPool(workers int) *MSTWorkerPool {
	return &MSTWorkerPool{workers: workers}
}

// ParallelEdgeSort implements parallel chunk sorting before final merge
// to accelerate Kruskal's algorithm on dense graphs.
func (p *MSTWorkerPool) ParallelEdgeSort(edges []Edge) OmniResult {
	if len(edges) == 0 {
		return OmniResult{Error: errors.New("empty edge list provided")}
	}

	chunkSize := len(edges) / p.workers
	if chunkSize == 0 {
		chunkSize = 1
	}

	var wg sync.WaitGroup
	chunks := make([][]Edge, p.workers)

	// Distribute work
	for i := 0; i < p.workers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if i == p.workers-1 {
			end = len(edges)
		}

		if start >= len(edges) {
			break
		}

		chunks[i] = edges[start:end]
		wg.Add(1)

		go func(idx int) {
			defer wg.Done()
			sort.Slice(chunks[idx], func(a, b int) bool {
				return chunks[idx][a].Weight < chunks[idx][b].Weight
			})
		}(i)
	}

	wg.Wait()

	// K-way merge (simplified via full sort for production reliability over complexity,
	// given Go's efficient sort implementation on pre-sorted chunks)
	// In strict zero-mock, we implement the actual merge logic.
	merged := make([]Edge, 0, len(edges))
	indices := make([]int, p.workers)

	for len(merged) < len(edges) {
		minIdx := -1
		minVal := -1.0

		for i := 0; i < p.workers; i++ {
			if indices[i] < len(chunks[i]) {
				val := chunks[i][indices[i]].Weight
				if minIdx == -1 || val < minVal {
					minIdx = i
					minVal = val
				}
			}
		}

		if minIdx != -1 {
			merged = append(merged, chunks[minIdx][indices[minIdx]])
			indices[minIdx]++
		} else {
			break // All chunks exhausted
		}
	}

	return OmniResult{Data: merged, Error: nil}
}
