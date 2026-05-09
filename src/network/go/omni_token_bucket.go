package network_go

import (
	"sync"
	"time"
)

// OMNI MOTHER: Token Bucket Rate Limiter
// Throttles incoming MoE requests to prevent expert OOM.

type TokenBucket struct {
	mu         sync.Mutex
	capacity   int
	tokens     int
	refillRate int // tokens per second
	lastRefill time.Time
}

func NewTokenBucket(capacity, refillRate int) *TokenBucket {
	return &TokenBucket{
		capacity:   capacity,
		tokens:     capacity,
		refillRate: refillRate,
		lastRefill: time.Now(),
	}
}

func (tb *TokenBucket) Allow(n int) bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()

	// Refill
	newTokens := int(elapsed * float64(tb.refillRate))
	if newTokens > 0 {
		tb.tokens += newTokens
		if tb.tokens > tb.capacity {
			tb.tokens = tb.capacity
		}
		tb.lastRefill = now
	}

	if tb.tokens >= n {
		tb.tokens -= n
		return true
	}

	return false
}

