package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type SearchQuery struct {
	QueryID string
	Vector  []float64
}

type IndexShards struct {
	shardCount int
	wg         sync.WaitGroup
}

func NewIndexShards(count int) *IndexShards {
	return &IndexShards{shardCount: count}
}

func (s *IndexShards) BroadcastQuery(query SearchQuery) OmniResult {
	if len(query.Vector) == 0 {
		return OmniResult{Error: fmt.Errorf("empty query vector")}
	}

	results := make(chan string, s.shardCount)

	// Fan-out query to all shards concurrently
	for i := 0; i < s.shardCount; i++ {
		s.wg.Add(1)
		go func(shardID int) {
			defer s.wg.Done()
			// Deterministic mock of shard search
			results <- fmt.Sprintf("Shard %d matched %d items", shardID, (shardID*3+7)%5)
		}(i)
	}

	// Wait in a separate goroutine so we can close the channel
	go func() {
		s.wg.Wait()
		close(results)
	}()

	// Collect aggregated results
	var aggregated []string
	for res := range results {
		aggregated = append(aggregated, res)
	}

	return OmniResult{Value: aggregated}
}
