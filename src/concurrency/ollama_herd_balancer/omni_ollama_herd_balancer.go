package ollama_herd

import (
	"errors"
	"sync"
	"sync/atomic"
	"time"
)

// OMNI Ollama Herd Balancer — Concurrency / Networking Layer
// Absorbing geeks-accelerator/ollama-herd: Local AI load balancer.
// Zero-mock, monadic implementation.

type HerdNode struct {
	ID        string
	Address   string
	Active    bool
	Load      int64
	MaxLoad   int64
	FailureCt int64
}

type HerdConfig struct {
	MaxFailures int64
	Timeout     time.Duration
}

type OmniOllamaHerdBalancer struct {
	mu       sync.RWMutex
	nodes    map[string]*HerdNode
	config   HerdConfig
	requests int64
}

func NewOmniOllamaHerdBalancer(cfg HerdConfig) *OmniOllamaHerdBalancer {
	if cfg.MaxFailures <= 0 {
		cfg.MaxFailures = 3
	}
	return &OmniOllamaHerdBalancer{
		nodes:  make(map[string]*HerdNode),
		config: cfg,
	}
}

func (h *OmniOllamaHerdBalancer) RegisterNode(id, address string, maxLoad int64) error {
	h.mu.Lock()
	defer h.mu.Unlock()
	if id == "" || address == "" {
		return errors.New("HerdError: Invalid node parameters")
	}
	h.nodes[id] = &HerdNode{ID: id, Address: address, Active: true, MaxLoad: maxLoad}
	return nil
}

// Selects the node with the lowest current load
func (h *OmniOllamaHerdBalancer) RouteRequest() (*HerdNode, error) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	var bestNode *HerdNode
	var minLoad int64 = -1

	for _, n := range h.nodes {
		if !n.Active {
			continue
		}
		currLoad := atomic.LoadInt64(&n.Load)
		if currLoad >= n.MaxLoad {
			continue
		}
		if minLoad == -1 || currLoad < minLoad {
			minLoad = currLoad
			bestNode = n
		}
	}

	if bestNode == nil {
		return nil, errors.New("HerdError: No available nodes")
	}

	atomic.AddInt64(&bestNode.Load, 1)
	atomic.AddInt64(&h.requests, 1)
	return bestNode, nil
}

func (h *OmniOllamaHerdBalancer) ReleaseNode(id string) error {
	h.mu.RLock()
	n, exists := h.nodes[id]
	h.mu.RUnlock()
	if !exists {
		return errors.New("HerdError: Node not found")
	}
	// Decrement load safely, floor at 0
	for {
		l := atomic.LoadInt64(&n.Load)
		if l == 0 {
			break
		}
		if atomic.CompareAndSwapInt64(&n.Load, l, l-1) {
			break
		}
	}
	return nil
}

func (h *OmniOllamaHerdBalancer) ReportFailure(id string) {
	h.mu.RLock()
	n, exists := h.nodes[id]
	h.mu.RUnlock()
	if exists {
		fails := atomic.AddInt64(&n.FailureCt, 1)
		if fails >= h.config.MaxFailures {
			n.Active = false
		}
		h.ReleaseNode(id)
	}
}

func (h *OmniOllamaHerdBalancer) Diagnostics() map[string]interface{} {
	h.mu.RLock()
	defer h.mu.RUnlock()

	activeCount := 0
	for _, n := range h.nodes {
		if n.Active {
			activeCount++
		}
	}

	return map[string]interface{}{
		"engine":       "OmniOllamaHerdBalancer",
		"total_nodes":  len(h.nodes),
		"active_nodes": activeCount,
		"requests":     atomic.LoadInt64(&h.requests),
		"status":       "Operational",
	}
}
