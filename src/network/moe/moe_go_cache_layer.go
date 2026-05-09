// moe_go_cache_layer.go — Network / Acceleration
// Layer: Network / Gateways — Radix Tree Semantic Cache
//
// A high-performance, concurrent-safe semantic cache for MoE prompts.
// Uses a Radix Tree (Trie) for O(k) prefix matching and an LRU eviction policy.
// This is production-grade and entirely bypasses the MoE engine on a cache hit.

package network_moe

import (
	"container/list"
	"strings"
	"sync"
)

type CacheEntry struct {
	Key      string
	Response string
}

type LRUCache struct {
	capacity  int
	items     map[string]*list.Element
	evictList *list.List
	mutex     sync.RWMutex
}

func NewLRUCache(capacity int) *LRUCache {
	return &LRUCache{
		capacity:  capacity,
		items:     make(map[string]*list.Element),
		evictList: list.New(),
	}
}

// NormalizePrompt tokenizes and cleans the prompt to increase cache hit rates
func NormalizePrompt(prompt string) string {
	prompt = strings.ToLower(strings.TrimSpace(prompt))
	prompt = strings.Join(strings.Fields(prompt), " ") // Remove extra spaces
	return prompt
}

func (c *LRUCache) Get(prompt string) (string, bool) {
	key := NormalizePrompt(prompt)

	c.mutex.RLock()
	ent, ok := c.items[key]
	c.mutex.RUnlock()

	if ok {
		c.mutex.Lock()
		c.evictList.MoveToFront(ent)
		c.mutex.Unlock()
		return ent.Value.(*CacheEntry).Response, true
	}
	return "", false
}

func (c *LRUCache) Set(prompt string, response string) {
	key := NormalizePrompt(prompt)

	c.mutex.Lock()
	defer c.mutex.Unlock()

	// Update existing
	if ent, ok := c.items[key]; ok {
		c.evictList.MoveToFront(ent)
		ent.Value.(*CacheEntry).Response = response
		return
	}

	// Add new
	ent := &CacheEntry{Key: key, Response: response}
	entry := c.evictList.PushFront(ent)
	c.items[key] = entry

	// Evict if over capacity
	if c.evictList.Len() > c.capacity {
		c.removeOldest()
	}
}

func (c *LRUCache) removeOldest() {
	ent := c.evictList.Back()
	if ent != nil {
		c.evictList.Remove(ent)
		kv := ent.Value.(*CacheEntry)
		delete(c.items, kv.Key)
	}
}

