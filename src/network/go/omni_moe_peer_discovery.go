package network_go

import (
	"log"
	"time"
)

// OMNI MOTHER: Gossip Protocol Peer Discovery
// Automatically detects new expert nodes joining the cluster

type PeerDiscovery struct {
	peers map[string]time.Time
}

func NewPeerDiscovery() *PeerDiscovery {
	return &PeerDiscovery{peers: make(map[string]time.Time)}
}

func (pd *PeerDiscovery) AnnouncePresence(ip string) {
	pd.peers[ip] = time.Now()
	log.Printf("[OMNI MOTHER] Peer discovered: %s", ip)
}

