package network_gocore

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"sync"
)

// DistributedCompilerCache speeds up OMNI universal binary builds by caching object files.
type DistributedCompilerCache struct {
	mu    sync.RWMutex
	cache map[string][]byte
}

func NewDistributedCompilerCache() *DistributedCompilerCache {
	return &DistributedCompilerCache{
		cache: make(map[string][]byte),
	}
}

func (c *DistributedCompilerCache) ComputeHash(sourceCode []byte) string {
	hash := sha256.Sum256(sourceCode)
	return hex.EncodeToString(hash[:])
}

func (c *DistributedCompilerCache) Get(ctx context.Context, hashKey string) ([]byte, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	data, exists := c.cache[hashKey]
	return data, exists
}

func (c *DistributedCompilerCache) Set(ctx context.Context, hashKey string, objectFile []byte) error {
	if hashKey == "" || len(objectFile) == 0 {
		return fmt.Errorf("invalid cache entry")
	}

	c.mu.Lock()
	defer c.mu.Unlock()
	c.cache[hashKey] = objectFile
	return nil
}

