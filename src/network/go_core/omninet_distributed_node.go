package network_gocore

import (
	"context"
	"fmt"
	"sync"
)

// OmninetDistributedNode handles routing of multidimensional sequences
// across the OMNI cluster for OmniNet processing.
type OmninetDistributedNode struct {
	mu       sync.RWMutex
	NodeID   string
	IsMaster bool
	Peers    []string
}

func NewOmninetDistributedNode(id string, master bool) *OmninetDistributedNode {
	return &OmninetDistributedNode{
		NodeID:   id,
		IsMaster: master,
		Peers:    make([]string, 0),
	}
}

func (n *OmninetDistributedNode) AddPeer(ctx context.Context, peerID string) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	for _, p := range n.Peers {
		if p == peerID {
			return fmt.Errorf("peer %s already exists", peerID)
		}
	}
	n.Peers = append(n.Peers, peerID)
	return nil
}

func (n *OmninetDistributedNode) BroadcastAttentionMask(ctx context.Context, mask []byte) error {
	n.mu.RLock()
	defer n.mu.RUnlock()

	if len(n.Peers) == 0 {
		return fmt.Errorf("no peers to broadcast to")
	}

	// OMNI gRPC simulation: send mask to all peers
	for _, peer := range n.Peers {
		_ = peer // send(peer, mask)
	}

	return nil
}

