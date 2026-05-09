package graphgpt

import (
	"errors"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type GraphWalker struct {
	MaxWorkers int
}

func (gw *GraphWalker) ParallelWalk(nodes []int) OmniResult {
	if len(nodes) == 0 {
		return OmniResult{Value: nil, Error: errors.New("empty nodes list")}
	}

	var wg sync.WaitGroup
	results := make(chan int, len(nodes))

	for _, node := range nodes {
		wg.Add(1)
		go func(n int) {
			defer wg.Done()
			results <- n * 2 // Production simulation of graph walking
		}(node)
	}

	wg.Wait()
	close(results)

	walked := make([]int, 0)
	for r := range results {
		walked = append(walked, r)
	}

	return OmniResult{Value: walked, Error: nil}
}
