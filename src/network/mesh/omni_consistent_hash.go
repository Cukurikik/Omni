package mesh

// omni_consistent_hash.go — Consistent Hashing Ring
// Layer: Network / Mesh / Routing
// Inspired by: groupcache / Cassandra
//
// Implements a consistent hashing ring to distribute traffic or data keys
// across a dynamically changing cluster of servers. Minimizes key re-mapping
// when a server joins or leaves the cluster (O(K/N) remapping instead of O(K)).
// Zero mock.

import (
	"hash/crc32"
	"sort"
	"strconv"
	"sync"
)

// Hash defines the hashing algorithm used for mapping.
type Hash func(data []byte) uint32

type OmniConsistentRing struct {
	mu       sync.RWMutex
	hash     Hash
	replicas int
	keys     []int          // Sorted array of hashes on the ring
	hashMap  map[int]string // Maps hash -> Node IP/ID
}

// NewOmniConsistentRing creates a new ring.
// `replicas` defines how many virtual nodes each physical node creates.
func NewOmniConsistentRing(replicas int, fn Hash) *OmniConsistentRing {
	m := &OmniConsistentRing{
		replicas: replicas,
		hash:     fn,
		hashMap:  make(map[int]string),
	}
	if m.hash == nil {
		m.hash = crc32.ChecksumIEEE
	}
	return m
}

// Add inserts physical nodes into the hash ring.
func (r *OmniConsistentRing) Add(nodes ...string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	for _, node := range nodes {
		for i := 0; i < r.replicas; i++ {
			// Generate virtual node ID
			hash := int(r.hash([]byte(strconv.Itoa(i) + node)))
			r.keys = append(r.keys, hash)
			r.hashMap[hash] = node
		}
	}
	// Keep the ring sorted for binary search
	sort.Ints(r.keys)
}

// Remove deletes a physical node and its virtual replicas from the ring.
func (r *OmniConsistentRing) Remove(node string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	for i := 0; i < r.replicas; i++ {
		hash := int(r.hash([]byte(strconv.Itoa(i) + node)))

		// Find index in keys slice
		idx := sort.SearchInts(r.keys, hash)
		if idx < len(r.keys) && r.keys[idx] == hash {
			// Remove from keys
			r.keys = append(r.keys[:idx], r.keys[idx+1:]...)
		}

		// Remove from map
		delete(r.hashMap, hash)
	}
}

// Get finds the closest node on the ring to the provided key.
func (r *OmniConsistentRing) Get(key string) string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.keys) == 0 {
		return ""
	}

	hash := int(r.hash([]byte(key)))

	// Binary search for the first virtual node hash >= the key's hash
	idx := sort.Search(len(r.keys), func(i int) bool {
		return r.keys[i] >= hash
	})

	// Wrap around to the first node if we've passed the last one
	if idx == len(r.keys) {
		idx = 0
	}

	return r.hashMap[r.keys[idx]]
}
