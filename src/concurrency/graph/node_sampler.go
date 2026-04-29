package graph

import (
	"time"
	"errors"
	"math/rand"
	"sync"
)

type Graph struct {
	AdjacencyList map[int][]int
}

type OmniResult struct {
	Walks [][]int
	Error error
}

type NodeSampler struct {
	graph      *Graph
	walkLength int
	numWalks   int
	workers    int
}

func NewNodeSampler(g *Graph, walkLength, numWalks, workers int) *NodeSampler {
	return &NodeSampler{
		graph:      g,
		walkLength: walkLength,
		numWalks:   numWalks,
		workers:    workers,
	}
}

// GenerateRandomWalks implements concurrent DeepWalk/Node2Vec style uniform random walks
func (s *NodeSampler) GenerateRandomWalks() OmniResult {
	if s.graph == nil || len(s.graph.AdjacencyList) == 0 {
		return OmniResult{Error: errors.New("empty graph")}
	}

	nodes := make([]int, 0, len(s.graph.AdjacencyList))
	for k := range s.graph.AdjacencyList {
		nodes = append(nodes, k)
	}

	totalWalks := len(nodes) * s.numWalks
	results := make([][]int, totalWalks)
	
	// Create job queue
	type Job struct {
		startNode int
		idx       int
	}
	
	jobs := make(chan Job, totalWalks)
	var wg sync.WaitGroup

	// Start worker pool
	for w := 0; w < s.workers; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			
			// Thread-local random generator to avoid global lock contention
			rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(workerID)))
			
			for job := range jobs {
				walk := make([]int, s.walkLength)
				curr := job.startNode
				walk[0] = curr

				for step := 1; step < s.walkLength; step++ {
					neighbors := s.graph.AdjacencyList[curr]
					if len(neighbors) == 0 {
						// Absorbing state if no neighbors
						break
					}
					
					// Uniform random sampling
					nextIdx := rng.Intn(len(neighbors))
					curr = neighbors[nextIdx]
					walk[step] = curr
				}
				results[job.idx] = walk
			}
		}(w)
	}

	// Dispatch jobs
	idx := 0
	for _, node := range nodes {
		for i := 0; i < s.numWalks; i++ {
			jobs <- Job{startNode: node, idx: idx}
			idx++
		}
	}
	
	close(jobs)
	wg.Wait()

	return OmniResult{Walks: results, Error: nil}
}
