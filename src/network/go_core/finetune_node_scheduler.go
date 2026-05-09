package network_gocore

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// FinetuneNodeScheduler handles the distributed scheduling of fine-tuning jobs.
type FinetuneNodeScheduler struct {
	mu          sync.RWMutex
	ActiveNodes map[string]NodeStatus
}

// NodeStatus represents the current state of a compute node.
type NodeStatus struct {
	NodeID   string
	GPUUtil  float64
	IsActive bool
	LastPing time.Time
}

// NewFinetuneNodeScheduler creates a new scheduler instance.
func NewFinetuneNodeScheduler() *FinetuneNodeScheduler {
	return &FinetuneNodeScheduler{
		ActiveNodes: make(map[string]NodeStatus),
	}
}

// RegisterNode adds a new node to the scheduler.
func (s *FinetuneNodeScheduler) RegisterNode(ctx context.Context, nodeID string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.ActiveNodes[nodeID]; exists {
		return fmt.Errorf("node %s already registered", nodeID)
	}

	s.ActiveNodes[nodeID] = NodeStatus{
		NodeID:   nodeID,
		GPUUtil:  0.0,
		IsActive: true,
		LastPing: time.Now(),
	}
	return nil
}

// GetAvailableNode returns the node with the lowest GPU utilization.
func (s *FinetuneNodeScheduler) GetAvailableNode(ctx context.Context) (string, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var bestNode string
	minUtil := 101.0

	for id, status := range s.ActiveNodes {
		if status.IsActive && status.GPUUtil < minUtil {
			minUtil = status.GPUUtil
			bestNode = id
		}
	}

	if bestNode == "" {
		return "", fmt.Errorf("no available nodes")
	}
	return bestNode, nil
}

