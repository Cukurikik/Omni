package network_go

import (
	"sync"
)

// OMNI MOTHER: Go PiKV Network Router
// Routes KV cache requests to the correct expert nodes via gRPC

type PiKVRouter struct {
	mu      sync.RWMutex
	nodeMap map[string]string // seqID -> nodeIP
}

func NewPiKVRouter() *PiKVRouter {
	return &PiKVRouter{
		nodeMap: make(map[string]string),
	}
}

func (r *PiKVRouter) RegisterSequence(seqID, nodeIP string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.nodeMap[seqID] = nodeIP
}

func (r *PiKVRouter) GetNodeForSequence(seqID string) (string, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	node, exists := r.nodeMap[seqID]
	return node, exists
}

