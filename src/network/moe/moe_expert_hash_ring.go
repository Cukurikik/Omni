// moe_expert_hash_ring.go — Network / Orchestration
// Layer: Network / Orchestration — Consistent Hashing
//
// When scaling MoE to a massive Kubernetes cluster, we need to know which
// physical Pod holds which Expert. This implements a Consistent Hash Ring
// to map Expert IDs to physical node IPs, minimizing reshuffling when nodes die.

package network_moe

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"sort"
	"sync"
)

type HashRingNode struct {
	Hash   uint32
	NodeIP string
}

type MoEExpertHashRing struct {
	mu           sync.RWMutex
	nodes        []HashRingNode
	virtualNodes int
}

func NewMoEExpertHashRing(virtualNodes int) *MoEExpertHashRing {
	fmt.Println("[MoE Hash Ring] Initialized Consistent Hashing Topology.")
	return &MoEExpertHashRing{
		virtualNodes: virtualNodes,
	}
}

func (r *MoEExpertHashRing) hashKey(key string) uint32 {
	hash := sha256.Sum256([]byte(key))
	return binary.BigEndian.Uint32(hash[0:4])
}

// AddNode registers a physical worker node (e.g., a GPU Pod)
func (r *MoEExpertHashRing) AddNode(ip string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	for i := 0; i < r.virtualNodes; i++ {
		vNodeKey := fmt.Sprintf("%s-v%d", ip, i)
		hash := r.hashKey(vNodeKey)
		r.nodes = append(r.nodes, HashRingNode{Hash: hash, NodeIP: ip})
	}

	// Keep ring sorted by hash
	sort.Slice(r.nodes, func(i, j int) bool {
		return r.nodes[i].Hash < r.nodes[j].Hash
	})
	// fmt.Printf("[MoE Hash Ring] Added Node %s to topology.\n", ip)
}

// GetNodeForExpert determines which IP currently hosts the requested Expert ID
func (r *MoEExpertHashRing) GetNodeForExpert(expertID int) string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.nodes) == 0 {
		return ""
	}

	expertKey := fmt.Sprintf("expert-%d", expertID)
	hash := r.hashKey(expertKey)

	// Binary search to find the first node with a hash >= the expert's hash
	idx := sort.Search(len(r.nodes), func(i int) bool {
		return r.nodes[i].Hash >= hash
	})

	// Wrap around to the first node if we went past the end
	if idx == len(r.nodes) {
		idx = 0
	}

	return r.nodes[idx].NodeIP
}

