package alpharec

import (
	"sync"

	"omni-engines/core/result"
)

type AlphaCache struct {
	store map[string][]byte
	mu    sync.RWMutex
}

func (c *AlphaCache) Get(key string) result.Result[[]byte] {
	c.mu.RLock()
	defer c.mu.RUnlock()
	if val, ok := c.store[key]; ok {
		return result.Ok(val)
	}
	return result.Err[[]byte](nil)
}
