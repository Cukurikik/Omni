package concurrency

import (
	"fmt"
	"hash/fnv"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type QueryRouter struct {
	nodeCount int
	nodes     []string
	mu        sync.RWMutex
}

func NewQueryRouter(nodes []string) *QueryRouter {
	return &QueryRouter{
		nodeCount: len(nodes),
		nodes:     nodes,
	}
}

// Deterministic consistent hashing math for routing
func (r *QueryRouter) hashEntity(entityID string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(entityID))
	return h.Sum32()
}

func (r *QueryRouter) RouteQuery(entityID string, featureName string) OmniResult {
	if entityID == "" || featureName == "" {
		return OmniResult{Error: fmt.Errorf("entityID and featureName are required")}
	}

	r.mu.RLock()
	defer r.mu.RUnlock()

	if r.nodeCount == 0 {
		return OmniResult{Error: fmt.Errorf("no feature nodes available")}
	}

	hashVal := r.hashEntity(entityID)
	nodeIdx := hashVal % uint32(r.nodeCount)
	targetNode := r.nodes[nodeIdx]

	// Simulate dispatch
	queryID := fmt.Sprintf("Q-%d-%s", hashVal, featureName)

	return OmniResult{Value: map[string]string{
		"query_id":    queryID,
		"target_node": targetNode,
		"entity_hash": fmt.Sprintf("%d", hashVal),
	}}
}
