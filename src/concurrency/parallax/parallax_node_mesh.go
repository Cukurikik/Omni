package concurrency

// Parallax Decentralized Node Discovery
// CSP-based peer mesh for pipeline-parallel inference

import (
	"time"
	"errors"
	"sync"
)

const MAX_NODES = 1024

type OmniResult struct {
	IsOk  bool
	Value interface{}
	Error error
}

type PeerNode struct {
	ID        string
	Address   string
	VRAMBytes uint64
	LastPing  time.Time
	Active    bool
}

type NodeMesh struct {
	nodes map[string]*PeerNode
	mu    sync.RWMutex
}

func NewNodeMesh() *NodeMesh {
	return &NodeMesh{nodes: make(map[string]*PeerNode)}
}

func (m *NodeMesh) Register(id, addr string, vram uint64) OmniResult {
	m.mu.Lock()
	defer m.mu.Unlock()
	if len(m.nodes) >= MAX_NODES {
		return OmniResult{IsOk: false, Error: errors.New("mesh capacity exhausted")}
	}
	m.nodes[id] = &PeerNode{ID: id, Address: addr, VRAMBytes: vram, LastPing: time.Now(), Active: true}
	return OmniResult{IsOk: true, Value: id}
}

func (m *NodeMesh) GetActiveNodes() OmniResult {
	m.mu.RLock()
	defer m.mu.RUnlock()
	active := make([]PeerNode, 0)
	for _, n := range m.nodes {
		if n.Active && time.Since(n.LastPing) < 30*time.Second {
			active = append(active, *n)
		}
	}
	return OmniResult{IsOk: true, Value: active}
}

func (m *NodeMesh) Heartbeat(id string) OmniResult {
	m.mu.Lock()
	defer m.mu.Unlock()
	if n, ok := m.nodes[id]; ok {
		n.LastPing = time.Now()
		n.Active = true
		return OmniResult{IsOk: true}
	}
	return OmniResult{IsOk: false, Error: errors.New("node not found")}
}
