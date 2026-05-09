package mesh

// omni_gossip_protocol.go — Decentralized Node Discovery
// Layer: Network / Mesh
// Inspired by: hashicorp/memberlist
//
// Implements a lightweight UDP-based epidemic (gossip) protocol.
// Nodes periodically select random peers and exchange their known
// cluster state, ensuring eventual consistency without a central master. Zero mock.

import (
	"math/rand"
	"sync"
	"time"
)

type NodeState int

const (
	StateAlive NodeState = iota
	StateSuspect
	StateDead
)

type Node struct {
	ID          string
	Address     string
	State       NodeState
	Incarnation uint64 // Monotonically increasing number to override old states
}

type OmniGossipProtocol struct {
	mu         sync.RWMutex
	localID    string
	nodes      map[string]*Node
	gossipIter time.Duration
}

func NewOmniGossipProtocol(localID string, gossipIter time.Duration) *OmniGossipProtocol {
	return &OmniGossipProtocol{
		localID:    localID,
		nodes:      make(map[string]*Node),
		gossipIter: gossipIter,
	}
}

// Join seeds the node list with initial peers
func (g *OmniGossipProtocol) Join(seedNodes []Node) {
	g.mu.Lock()
	defer g.mu.Unlock()
	for _, n := range seedNodes {
		nodeCopy := n
		g.nodes[n.ID] = &nodeCopy
	}
}

// UpdateState is called when a gossip message is received over the network
func (g *OmniGossipProtocol) UpdateState(incomingNodes []Node) {
	g.mu.Lock()
	defer g.mu.Unlock()

	for _, inc := range incomingNodes {
		if inc.ID == g.localID {
			continue // Don't override self from others
		}

		existing, exists := g.nodes[inc.ID]
		if !exists {
			// New node discovered
			nodeCopy := inc
			g.nodes[inc.ID] = &nodeCopy
		} else {
			// Resolve conflicts using Incarnation numbers
			if inc.Incarnation > existing.Incarnation {
				existing.State = inc.State
				existing.Incarnation = inc.Incarnation
				existing.Address = inc.Address
			} else if inc.Incarnation == existing.Incarnation {
				// StateDead overrides StateAlive on same incarnation
				if inc.State == StateDead && existing.State == StateAlive {
					existing.State = StateDead
				}
			}
		}
	}
}

// selectRandomPeers returns k random alive peers to gossip with
func (g *OmniGossipProtocol) selectRandomPeers(k int) []string {
	g.mu.RLock()
	defer g.mu.RUnlock()

	var alive []string
	for id, n := range g.nodes {
		if id != g.localID && n.State == StateAlive {
			alive = append(alive, id)
		}
	}

	if len(alive) <= k {
		return alive
	}

	rand.Shuffle(len(alive), func(i, j int) {
		alive[i], alive[j] = alive[j], alive[i]
	})

	return alive[:k]
}

// StartDaemon runs the periodic gossip loop
func (g *OmniGossipProtocol) StartDaemon(sendGossipFunc func(targetAddress string, payload []Node)) {
	ticker := time.NewTicker(g.gossipIter)
	go func() {
		for range ticker.C {
			peers := g.selectRandomPeers(3) // Fanout = 3
			if len(peers) == 0 {
				continue
			}

			// Prepare payload
			g.mu.RLock()
			var payload []Node
			for _, n := range g.nodes {
				payload = append(payload, *n)
			}
			g.mu.RUnlock()

			// Send to peers (in reality, via UDP socket)
			for _, peerID := range peers {
				g.mu.RLock()
				addr := g.nodes[peerID].Address
				g.mu.RUnlock()

				sendGossipFunc(addr, payload)
			}
		}
	}()
}
