package network_go

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net"
	"sync"
	"time"
)

// OMNI MOTHER: P2P Gossip Protocol
// Decentralized discovery and health tracking of Expert Nodes.

type NodeState struct {
	IP          string
	Port        int
	Status      string
	LastUpdated int64
}

type GossipManager struct {
	Nodes    map[string]NodeState
	mu       sync.RWMutex
	bindPort int
}

func NewGossipManager(port int) *GossipManager {
	return &GossipManager{
		Nodes:    make(map[string]NodeState),
		bindPort: port,
	}
}

func (g *GossipManager) Start() {
	addr := net.UDPAddr{
		Port: g.bindPort,
		IP:   net.ParseIP("0.0.0.0"),
	}
	conn, err := net.ListenUDP("udp", &addr)
	if err != nil {
		log.Fatalf("OMNI ERROR: Failed to start Gossip listener: %v", err)
	}

	go g.listen(conn)
	go g.gossipLoop(conn)
}

func (g *GossipManager) listen(conn *net.UDPConn) {
	buf := make([]byte, 2048)
	for {
		n, _, err := conn.ReadFromUDP(buf)
		if err != nil {
			continue
		}

		var incomingNodes map[string]NodeState
		if err := json.Unmarshal(buf[:n], &incomingNodes); err == nil {
			g.merge(incomingNodes)
		}
	}
}

func (g *GossipManager) gossipLoop(conn *net.UDPConn) {
	ticker := time.NewTicker(2 * time.Second)
	for range ticker.C {
		g.mu.RLock()
		if len(g.Nodes) == 0 {
			g.mu.RUnlock()
			continue
		}

		// Pick random node to gossip with
		keys := make([]string, 0, len(g.Nodes))
		for k := range g.Nodes {
			keys = append(keys, k)
		}
		target := g.Nodes[keys[rand.Intn(len(keys))]]

		payload, _ := json.Marshal(g.Nodes)
		g.mu.RUnlock()

		targetAddr, _ := net.ResolveUDPAddr("udp", fmt.Sprintf("%s:%d", target.IP, target.Port))
		conn.WriteToUDP(payload, targetAddr)
	}
}

func (g *GossipManager) merge(incoming map[string]NodeState) {
	g.mu.Lock()
	defer g.mu.Unlock()
	for id, state := range incoming {
		if existing, ok := g.Nodes[id]; !ok || state.LastUpdated > existing.LastUpdated {
			g.Nodes[id] = state
		}
	}
}

