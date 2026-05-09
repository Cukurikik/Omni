// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Halfrost Hasher (OMNI Zero-Mock Implementation)
// Implements Consistent Hashing Ring mathematically.

package compute

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"fmt"
	"sort"
)

type HashRingResult struct {
	Value string
	Error error
}

func OkHashRingResult(val string) HashRingResult {
	return HashRingResult{Value: val, Error: nil}
}

func ErrHashRingResult(err string) HashRingResult {
	return HashRingResult{Value: "", Error: errors.New(err)}
}

type NodeHash struct {
	Hash uint32
	Node string
}

type ConsistentHashRing struct {
	nodes    []NodeHash
	replicas int
}

func NewConsistentHashRing(replicas int) *ConsistentHashRing {
	return &ConsistentHashRing{
		replicas: replicas,
	}
}

func (c *ConsistentHashRing) getRawHash(key string) uint32 {
	h := sha256.New()
	h.Write([]byte(key))
	sum := h.Sum(nil)
	return binary.BigEndian.Uint32(sum[:4])
}

func (c *ConsistentHashRing) AddNode(node string) {
	for i := 0; i < c.replicas; i++ {
		replicaKey := fmt.Sprintf("%s:%d", node, i)
		hash := c.getRawHash(replicaKey)
		c.nodes = append(c.nodes, NodeHash{Hash: hash, Node: node})
	}

	// Sort by hash to form the ring
	sort.Slice(c.nodes, func(i, j int) bool {
		return c.nodes[i].Hash < c.nodes[j].Hash
	})
}

func (c *ConsistentHashRing) GetNode(key string) HashRingResult {
	if len(c.nodes) == 0 {
		return ErrHashRingResult("Hash ring is empty.")
	}

	hash := c.getRawHash(key)

	// Binary search to find the first node with hash >= request hash
	idx := sort.Search(len(c.nodes), func(i int) bool {
		return c.nodes[i].Hash >= hash
	})

	// Wrap around the ring
	if idx >= len(c.nodes) {
		idx = 0
	}

	return OkHashRingResult(c.nodes[idx].Node)
}
