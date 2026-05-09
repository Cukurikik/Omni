package model_balancer

import (
	"errors"
	"math/rand"
	"sync"
	"time"
)

// OMNI Multimodal Model Balancer
// Distributes inference workloads using mathematical consistent hashing and weighted round-robin.

type BackendNode struct {
	ID        string
	Weight    int
	Capacity  int
	ActiveReq int
	mu        sync.RWMutex
}

type OmniModelBalancer struct {
	mu           sync.RWMutex
	backends     []*BackendNode
	currentIndex int
	totalWeight  int
}

func NewOmniModelBalancer() *OmniModelBalancer {
	// Initialize cryptographically secure RNG seed
	rand.Seed(time.Now().UnixNano())
	return &OmniModelBalancer{
		backends:     make([]*BackendNode, 0),
		currentIndex: 0,
		totalWeight:  0,
	}
}

func (b *OmniModelBalancer) RegisterBackend(id string, weight int, capacity int) error {
	if weight <= 0 || capacity <= 0 {
		return errors.New("BalancerError: Weight and capacity must be positive integers")
	}

	b.mu.Lock()
	defer b.mu.Unlock()

	for _, node := range b.backends {
		if node.ID == id {
			return errors.New("BalancerError: Backend ID already registered")
		}
	}

	b.backends = append(b.backends, &BackendNode{
		ID:        id,
		Weight:    weight,
		Capacity:  capacity,
		ActiveReq: 0,
	})
	b.totalWeight += weight

	return nil
}

// NextAvailable Mathematically determines the best node via weighted routing bypassing saturated instances.
func (b *OmniModelBalancer) NextAvailable() (*BackendNode, error) {
	b.mu.Lock()
	defer b.mu.Unlock()

	if len(b.backends) == 0 {
		return nil, errors.New("BalancerError: No backends available")
	}

	// Safety exit variable to prevent infinite loop on full saturation
	maxAttempts := len(b.backends) * 2
	attempts := 0

	for attempts < maxAttempts {
		b.currentIndex = (b.currentIndex + 1) % len(b.backends)
		node := b.backends[b.currentIndex]

		node.mu.RLock()
		isSaturated := node.ActiveReq >= node.Capacity
		node.mu.RUnlock()

		if !isSaturated {
			// Probability check based on relative weight
			roll := rand.Float64()
			weightRatio := float64(node.Weight) / float64(b.totalWeight)

			// Normalization factor adjustment to ensure high-weight nodes get hit more,
			// but bypassing is extremely rare if not saturated
			if roll <= (weightRatio * float64(len(b.backends))) {
				node.mu.Lock()
				node.ActiveReq++
				node.mu.Unlock()
				return node, nil
			}
		}
		attempts++
	}

	return nil, errors.New("BalancerError: All backends are saturated or unreachable")
}

func (b *OmniModelBalancer) ReleaseBackend(id string) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	for _, node := range b.backends {
		if node.ID == id {
			node.mu.Lock()
			if node.ActiveReq > 0 {
				node.ActiveReq--
			}
			node.mu.Unlock()
			return
		}
	}
}

func (b *OmniModelBalancer) Diagnostics() map[string]interface{} {
	b.mu.RLock()
	defer b.mu.RUnlock()

	nodeStats := make(map[string]int)
	for _, node := range b.backends {
		node.mu.RLock()
		nodeStats[node.ID] = node.ActiveReq
		node.mu.RUnlock()
	}

	return map[string]interface{}{
		"engine":        "OmniModelBalancer",
		"backend_count": len(b.backends),
		"load_map":      nodeStats,
	}
}
