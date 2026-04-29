package mace

import (
	"context"
	"errors"
	"sync"
	"time"
)

// OMNI Concurrency Layer: MACE Model Mesh Router (Go)
// Manages offloading mobile inference tasks to edge nodes dynamically.

type EdgeNode struct {
	ID        string
	IPAddress string
	Load      int
	LastSeen  time.Time
}

type ModelMeshRouter struct {
	mu    sync.RWMutex
	nodes map[string]*EdgeNode
}

func NewModelMeshRouter() *ModelMeshRouter {
	return &ModelMeshRouter{
		nodes: make(map[string]*EdgeNode),
	}
}

func (r *ModelMeshRouter) RegisterNode(id, ip string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.nodes[id] = &EdgeNode{
		ID:        id,
		IPAddress: ip,
		Load:      0,
		LastSeen:  time.Now(),
	}
}

func (r *ModelMeshRouter) Heartbeat(id string, currentLoad int) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	node, exists := r.nodes[id]
	if !exists {
		return errors.New("node not registered")
	}
	node.Load = currentLoad
	node.LastSeen = time.Now()
	return nil
}

func (r *ModelMeshRouter) RouteInferenceTask(ctx context.Context, modelID string) (*EdgeNode, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	var bestNode *EdgeNode
	lowestLoad := int(^uint(0) >> 1) // Max int

	threshold := time.Now().Add(-30 * time.Second)

	for _, node := range r.nodes {
		if node.LastSeen.After(threshold) && node.Load < lowestLoad {
			bestNode = node
			lowestLoad = node.Load
		}
	}

	if bestNode == nil {
		return nil, errors.New("no healthy edge nodes available")
	}

	return bestNode, nil
}
