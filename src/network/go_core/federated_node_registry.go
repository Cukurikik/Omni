package network_gocore

import (
	"context"
	"sync"
	"time"
)

// FederatedNodeRegistry tracks edge devices participating in FL.
type FederatedNodeRegistry struct {
	mu    sync.RWMutex
	Nodes map[string]*EdgeNode
}

type EdgeNode struct {
	DeviceID      string
	HardwareSpecs string
	LastPing      time.Time
	Status        string
}

func NewFederatedNodeRegistry() *FederatedNodeRegistry {
	return &FederatedNodeRegistry{
		Nodes: make(map[string]*EdgeNode),
	}
}

func (r *FederatedNodeRegistry) RegisterNode(ctx context.Context, id, specs string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.Nodes[id] = &EdgeNode{
		DeviceID:      id,
		HardwareSpecs: specs,
		LastPing:      time.Now(),
		Status:        "ONLINE",
	}
	return nil
}

func (r *FederatedNodeRegistry) GetActiveNodesCount() int {
	r.mu.RLock()
	defer r.mu.RUnlock()

	count := 0
	now := time.Now()
	for _, n := range r.Nodes {
		if now.Sub(n.LastPing) < 5*time.Minute {
			count++
		}
	}
	return count
}

