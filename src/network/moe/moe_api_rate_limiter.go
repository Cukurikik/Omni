// moe_api_rate_limiter.go — Network / Security
// Layer: Network / Gateways — Token Bucket Rate Limiter
//
// A production-grade Token Bucket rate limiter to protect the MoE Inference
// Gateway from DDoS attacks or runaway API clients. Tracks limits per TenantID.

package network_moe

import (
	"fmt"
	"sync"
	"time"
)

type TokenBucket struct {
	Capacity     float64
	Tokens       float64
	RefillRate   float64 // Tokens per second
	LastRefilled time.Time
	mu           sync.Mutex
}

type RateLimiter struct {
	buckets map[string]*TokenBucket
	mu      sync.RWMutex
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		buckets: make(map[string]*TokenBucket),
	}
}

// GetBucket retrieves or creates a token bucket for a specific tenant
func (rl *RateLimiter) GetBucket(tenantID string, capacity float64, refillRate float64) *TokenBucket {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	bucket, exists := rl.buckets[tenantID]
	if !exists {
		bucket = &TokenBucket{
			Capacity:     capacity,
			Tokens:       capacity,
			RefillRate:   refillRate,
			LastRefilled: time.Now(),
		}
		rl.buckets[tenantID] = bucket
	}
	return bucket
}

// Allow checks if the request can proceed and deducts the requested tokens
func (tb *TokenBucket) Allow(requestedTokens float64) bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.LastRefilled).Seconds()

	// Refill tokens based on elapsed time
	tb.Tokens += elapsed * tb.RefillRate
	if tb.Tokens > tb.Capacity {
		tb.Tokens = tb.Capacity
	}
	tb.LastRefilled = now

	if tb.Tokens >= requestedTokens {
		tb.Tokens -= requestedTokens
		return true
	}

	return false
}

// Middleware wrapper for HTTP handlers
func (rl *RateLimiter) EnforceRateLimit(tenantID string, requestedTokens float64) error {
	// Standard tier: 10,000 tokens capacity, refills at 500 tokens/sec
	bucket := rl.GetBucket(tenantID, 10000.0, 500.0)

	if !bucket.Allow(requestedTokens) {
		return fmt.Errorf("HTTP 429 Too Many Requests: Tenant %s exceeded MoE API token limits", tenantID)
	}
	return nil
}

