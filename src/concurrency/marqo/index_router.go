package marqo

import (
	"errors"
	"context"
	"hash/fnv"
	"sync"
)

// OMNI Concurrency Layer: Marqo Indexing Router (Go)
// Distributes vector shards across index nodes utilizing consistent hashing.

type ShardNode struct {
	NodeID   string
	Address  string
	IsActive bool
}

type IndexRouter struct {
	mu    sync.RWMutex
	nodes []ShardNode
}

func NewIndexRouter(initialNodes []ShardNode) *IndexRouter {
	return &IndexRouter{
		nodes: initialNodes,
	}
}

func (r *IndexRouter) hashKey(key string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(key))
	return h.Sum32()
}

func (r *IndexRouter) RouteDocument(ctx context.Context, documentID string) (*ShardNode, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.nodes) == 0 {
		return nil, errors.New("no active shard nodes available")
	}

	// Consistent hashing ring distribution
	hash := r.hashKey(documentID)
	nodeIndex := hash % uint32(len(r.nodes))

	node := &r.nodes[nodeIndex]
	if !node.IsActive {
		return nil, errors.New("target shard node is currently inactive")
	}

	return node, nil
}

func (r *IndexRouter) AddNode(node ShardNode) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.nodes = append(r.nodes, node)
}

func (r *IndexRouter) RemoveNode(nodeID string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	for i, n := range r.nodes {
		if n.NodeID == nodeID {
			r.nodes = append(r.nodes[:i], r.nodes[i+1:]...)
			break
		}
	}
}
