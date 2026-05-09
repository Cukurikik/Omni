// moe_p2p_mesh.go — Peer-to-Peer Mesh for MoE Discovery
// Layer: Network / P2P — MoE Cluster Topology
//
// Manages a dynamic peer-to-peer mesh network for MoE nodes.
// Handles auto-discovery of nodes hosting specific experts, routing
// table updates, and mesh topology maintenance without a central registry.

package network_moe

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// ExpertLocation maps an expert ID to the node ID currently hosting it.
type ExpertLocation struct {
	ExpertID int32
	NodeID   string
	Address  string
	Status   string // "active", "warming_up", "draining"
}

// MoEP2PMesh maintains the routing table for distributed experts.
type MoEP2PMesh struct {
	localNodeID string
	localAddr   string

	// Map expert ID -> Location
	routingTable map[int32]ExpertLocation

	// Map Node ID -> last seen time
	peers map[string]time.Time

	mu sync.RWMutex
}

func NewMoEP2PMesh(nodeID, address string) *MoEP2PMesh {
	return &MoEP2PMesh{
		localNodeID:  nodeID,
		localAddr:    address,
		routingTable: make(map[int32]ExpertLocation),
		peers:        make(map[string]time.Time),
	}
}

// AnnounceExperts broadcasts to the mesh that this node hosts certain experts.
func (m *MoEP2PMesh) AnnounceExperts(expertIDs []int32) {
	m.mu.Lock()
	defer m.mu.Unlock()

	for _, eid := range expertIDs {
		m.routingTable[eid] = ExpertLocation{
			ExpertID: eid,
			NodeID:   m.localNodeID,
			Address:  m.localAddr,
			Status:   "active",
		}
	}

	// In production: Broadcast via UDP multicast or gossip protocol
	// fmt.Printf("Node %s announced experts %v\n", m.localNodeID, expertIDs)
}

// HandlePeerAnnouncement processes an announcement from another node.
func (m *MoEP2PMesh) HandlePeerAnnouncement(peerID, peerAddr string, expertIDs []int32) {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.peers[peerID] = time.Now()

	for _, eid := range expertIDs {
		m.routingTable[eid] = ExpertLocation{
			ExpertID: eid,
			NodeID:   peerID,
			Address:  peerAddr,
			Status:   "active",
		}
	}
}

// GetExpertRoute resolves an expert ID to a network address.
func (m *MoEP2PMesh) GetExpertRoute(expertID int32) (string, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()

	loc, exists := m.routingTable[expertID]
	if !exists {
		return "", fmt.Errorf("route not found for expert %d", expertID)
	}

	if loc.Status != "active" {
		return "", fmt.Errorf("expert %d is %s", expertID, loc.Status)
	}

	return loc.Address, nil
}

// GetBatchRoutes resolves addresses for a batch of experts.
func (m *MoEP2PMesh) GetBatchRoutes(expertIDs []int32) map[int32]string {
	m.mu.RLock()
	defer m.mu.RUnlock()

	routes := make(map[int32]string)
	for _, eid := range expertIDs {
		if loc, exists := m.routingTable[eid]; exists && loc.Status == "active" {
			routes[eid] = loc.Address
		}
	}
	return routes
}

// PruneStalePeers removes peers that haven't been seen recently.
func (m *MoEP2PMesh) PruneStalePeers(ctx context.Context, timeout time.Duration) {
	ticker := time.NewTicker(timeout / 2)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			m.mu.Lock()
			now := time.Now()
			for peerID, lastSeen := range m.peers {
				if now.Sub(lastSeen) > timeout {
					delete(m.peers, peerID)
					// Remove experts hosted by this peer
					for eid, loc := range m.routingTable {
						if loc.NodeID == peerID {
							delete(m.routingTable, eid)
						}
					}
				}
			}
			m.mu.Unlock()
		}
	}
}

