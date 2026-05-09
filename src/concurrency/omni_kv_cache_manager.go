// OMNI Engine — Prompt Caching & KV Cache Manager (Go)
// Implements: Prefix caching, radix tree routing, cache eviction, memory estimation
package concurrency

type CacheEntry struct {
	Prefix string
}
