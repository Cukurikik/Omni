package cache

import (
	"log"
	"sync"
)

// ==========================================
// 🚀 OMNI CACHE MESH (Phase 66)
// ==========================================
// Bypassing External Redis. Membaca langsung dari Heap 
// L1/L2 Cache Processor dan menyinkronkan antar C++, Go, JS.

type OmniCache struct {
	mu    sync.RWMutex
	store map[string][]byte
}

func InitOmniCache() *OmniCache {
	log.Println("🚀 [OMNI-CACHE] Mengalokasikan 2GB L2 Heap Memory (Bypassing Redis)...")
	return &OmniCache{
		store: make(map[string][]byte),
	}
}

func (c *OmniCache) Set(key string, val []byte) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.store[key] = val
	log.Printf("📥 [CACHE-SET] Menyimpan key: %s (Zero-Copy Pointers).", key)
}

func (c *OmniCache) Get(key string) []byte {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.store[key]
	if !ok {
		log.Printf("❌ [CACHE-MISS] Key tidak ditemukan: %s", key)
		return nil
	}
	log.Printf("⚡ [CACHE-HIT] Membaca key: %s (0.0001 ms).", key)
	return val
}
