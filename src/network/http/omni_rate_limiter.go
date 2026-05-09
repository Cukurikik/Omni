package network_http

// omni_rate_limiter.go — Token Bucket Rate Limiter
// Layer: Network / Go
//
// Implements a high-performance, concurrent token bucket rate limiter
// to protect OMNI REST and gRPC gateways from abuse. Zero mock.

import (
	"sync"
	"time"
)

type TokenBucket struct {
	capacity   float64
	tokens     float64
	fillRate   float64 // tokens per second
	lastUpdate time.Time
	mu         sync.Mutex
}

func NewTokenBucket(capacity float64, fillRate float64) *TokenBucket {
	return &TokenBucket{
		capacity:   capacity,
		tokens:     capacity,
		fillRate:   fillRate,
		lastUpdate: time.Now(),
	}
}

// Allow checks if 'n' tokens can be consumed.
func (tb *TokenBucket) Allow(n float64) bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastUpdate).Seconds()

	// Replenish tokens based on elapsed time
	tb.tokens += elapsed * tb.fillRate
	if tb.tokens > tb.capacity {
		tb.tokens = tb.capacity
	}
	tb.lastUpdate = now

	// Check if enough tokens exist
	if tb.tokens >= n {
		tb.tokens -= n
		return true
	}

	return false
}

// OmniRateLimiter manages token buckets for multiple clients (e.g., by IP).
type OmniRateLimiter struct {
	buckets  map[string]*TokenBucket
	capacity float64
	fillRate float64
	mu       sync.RWMutex
}

func NewOmniRateLimiter(capacity float64, fillRate float64) *OmniRateLimiter {
	return &OmniRateLimiter{
		buckets:  make(map[string]*TokenBucket),
		capacity: capacity,
		fillRate: fillRate,
	}
}

// AllowClient determines if a specific client ID is permitted to proceed.
func (rl *OmniRateLimiter) AllowClient(clientID string) bool {
	rl.mu.RLock()
	bucket, exists := rl.buckets[clientID]
	rl.mu.RUnlock()

	if !exists {
		rl.mu.Lock()
		// Double check locking
		bucket, exists = rl.buckets[clientID]
		if !exists {
			bucket = NewTokenBucket(rl.capacity, rl.fillRate)
			rl.buckets[clientID] = bucket
		}
		rl.mu.Unlock()
	}

	return bucket.Allow(1.0)
}

// CleanOldBuckets could be implemented here as a background goroutine
// to prevent memory leaks from one-time visitors.

