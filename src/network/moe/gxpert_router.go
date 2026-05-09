// gxpert_router.go — Network / Orchestration
// Layer: Network / Gateways — GXpert Deterministic Routing
//
// Inspired by the GXpert architecture.
// A Go-based network orchestrator that manages MoE inference requests
// at the cluster level. Ensures that identical prompts hit the same
// physical GPU nodes to maximize prefix-cache hits and avoid VRAM thrashing.

package network_moe

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"sync"
)

// ExpertNode represents a physical GPU or worker holding specific experts
type ExpertNode struct {
	ID        string
	IPAddress string
	VRAMFree  int64
	ExpertIDs []int
}

// GXpertRouter manages traffic distribution
type GXpertRouter struct {
	mu        sync.RWMutex
	nodes     map[string]*ExpertNode
	expertMap map[int][]*ExpertNode // ExpertID -> List of Nodes hosting it
}

func NewGXpertRouter() *GXpertRouter {
	fmt.Println("[GXpert] Initializing MoE Cluster Router...")
	return &GXpertRouter{
		nodes:     make(map[string]*ExpertNode),
		expertMap: make(map[int][]*ExpertNode),
	}
}

// RegisterNode adds a new worker node to the cluster
func (r *GXpertRouter) RegisterNode(node *ExpertNode) {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.nodes[node.ID] = node
	for _, expID := range node.ExpertIDs {
		r.expertMap[expID] = append(r.expertMap[expID], node)
	}
	fmt.Printf("[GXpert] Registered Node %s hosting %d experts.\n", node.ID, len(node.ExpertIDs))
}

// RoutePrompt calculates a deterministic route based on prompt hash to maximize cache hits
func (r *GXpertRouter) RoutePrompt(promptText string) (*ExpertNode, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.nodes) == 0 {
		return nil, fmt.Errorf("no active nodes in the cluster")
	}

	// Calculate deterministic hash of the prompt
	hash := sha256.Sum256([]byte(promptText))
	hashString := hex.EncodeToString(hash[:])

	// Simple Consistent Hashing (Modulo based for zero-mock standalone logic)
	// In production, a proper HashRing algorithm is used to prevent massive reshuffling
	var targetNode *ExpertNode
	nodeList := make([]*ExpertNode, 0, len(r.nodes))
	for _, n := range r.nodes {
		nodeList = append(nodeList, n)
	}

	// Calculate integer from first 4 bytes of hash
	hashInt := int(hash[0])<<24 | int(hash[1])<<16 | int(hash[2])<<8 | int(hash[3])
	idx := uint(hashInt) % uint(len(nodeList))

	targetNode = nodeList[idx]

	fmt.Printf("[GXpert] Routed prompt (hash %s...) to Node %s\n", hashString[:8], targetNode.ID)
	return targetNode, nil
}

