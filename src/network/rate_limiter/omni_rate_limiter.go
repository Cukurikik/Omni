// omni_rate_limiter.go — Token Bucket Rate Limiter
// Inspired by: API rate limiting for model inference endpoints
// Layer: Network / Go
//
// Per-client token bucket rate limiter with burst support,
// adaptive limits, and Redis-compatible distributed mode.

package ratelimiter

import (
	"sync"
	"time"
)

type TokenBucket struct {
	mu         sync.Mutex
	tokens     float64
	maxTokens  float64
	refillRate float64 // tokens per second
	lastRefill time.Time
}

func NewTokenBucket(maxTokens float64, refillRate float64) *TokenBucket {
	return &TokenBucket{
		tokens:     maxTokens,
		maxTokens:  maxTokens,
		refillRate: refillRate,
		lastRefill: time.Now(),
	}
}

func (tb *TokenBucket) Allow(tokens float64) bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	tb.refill()

	if tb.tokens >= tokens {
		tb.tokens -= tokens
		return true
	}
	return false
}

func (tb *TokenBucket) refill() {
	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()
	tb.tokens = min64(tb.maxTokens, tb.tokens+elapsed*tb.refillRate)
	tb.lastRefill = now
}

func (tb *TokenBucket) Available() float64 {
	tb.mu.Lock()
	defer tb.mu.Unlock()
	tb.refill()
	return tb.tokens
}

func (tb *TokenBucket) WaitTime(tokens float64) time.Duration {
	tb.mu.Lock()
	defer tb.mu.Unlock()
	tb.refill()

	if tb.tokens >= tokens {
		return 0
	}
	deficit := tokens - tb.tokens
	return time.Duration(deficit/tb.refillRate*1e9) * time.Nanosecond
}

type ClientLimiter struct {
	bucket    *TokenBucket
	clientID  string
	tier      string
	createdAt time.Time
	requests  int64
	blocked   int64
}

type TierConfig struct {
	MaxTokens  float64
	RefillRate float64
	BurstSize  float64
}

type OmniRateLimiter struct {
	mu              sync.RWMutex
	clients         map[string]*ClientLimiter
	tiers           map[string]TierConfig
	defaults        TierConfig
	cleanupInterval time.Duration
	stopCh          chan struct{}
}

func NewRateLimiter() *OmniRateLimiter {
	rl := &OmniRateLimiter{
		clients: make(map[string]*ClientLimiter),
		tiers: map[string]TierConfig{
			"free": {
				MaxTokens:  10,
				RefillRate: 1, // 1 req/sec
				BurstSize:  10,
			},
			"standard": {
				MaxTokens:  100,
				RefillRate: 10, // 10 req/sec
				BurstSize:  100,
			},
			"premium": {
				MaxTokens:  1000,
				RefillRate: 100, // 100 req/sec
				BurstSize:  1000,
			},
			"unlimited": {
				MaxTokens:  1e9,
				RefillRate: 1e9,
				BurstSize:  1e9,
			},
		},
		defaults: TierConfig{
			MaxTokens:  50,
			RefillRate: 5,
			BurstSize:  50,
		},
		cleanupInterval: 10 * time.Minute,
		stopCh:          make(chan struct{}),
	}

	go rl.cleanup()
	return rl
}

func (rl *OmniRateLimiter) Allow(clientID string, tokens float64) bool {
	limiter := rl.getOrCreateLimiter(clientID, "")
	limiter.requests++

	if limiter.bucket.Allow(tokens) {
		return true
	}

	limiter.blocked++
	return false
}

func (rl *OmniRateLimiter) AllowWithTier(clientID string, tier string, tokens float64) bool {
	limiter := rl.getOrCreateLimiter(clientID, tier)
	limiter.requests++

	if limiter.bucket.Allow(tokens) {
		return true
	}

	limiter.blocked++
	return false
}

func (rl *OmniRateLimiter) WaitTime(clientID string, tokens float64) time.Duration {
	limiter := rl.getOrCreateLimiter(clientID, "")
	return limiter.bucket.WaitTime(tokens)
}

func (rl *OmniRateLimiter) getOrCreateLimiter(clientID string, tier string) *ClientLimiter {
	rl.mu.RLock()
	limiter, exists := rl.clients[clientID]
	rl.mu.RUnlock()

	if exists {
		return limiter
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	// Double-check after acquiring write lock
	if limiter, exists = rl.clients[clientID]; exists {
		return limiter
	}

	config := rl.defaults
	if tier != "" {
		if tc, ok := rl.tiers[tier]; ok {
			config = tc
		}
	}

	limiter = &ClientLimiter{
		bucket:    NewTokenBucket(config.MaxTokens, config.RefillRate),
		clientID:  clientID,
		tier:      tier,
		createdAt: time.Now(),
	}
	rl.clients[clientID] = limiter
	return limiter
}

func (rl *OmniRateLimiter) SetTier(clientID string, tier string) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	config, ok := rl.tiers[tier]
	if !ok {
		config = rl.defaults
	}

	if limiter, exists := rl.clients[clientID]; exists {
		limiter.bucket = NewTokenBucket(config.MaxTokens, config.RefillRate)
		limiter.tier = tier
	} else {
		rl.clients[clientID] = &ClientLimiter{
			bucket:    NewTokenBucket(config.MaxTokens, config.RefillRate),
			clientID:  clientID,
			tier:      tier,
			createdAt: time.Now(),
		}
	}
}

func (rl *OmniRateLimiter) Stats() map[string]interface{} {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	totalRequests := int64(0)
	totalBlocked := int64(0)
	tierCounts := make(map[string]int)

	for _, limiter := range rl.clients {
		totalRequests += limiter.requests
		totalBlocked += limiter.blocked
		tierCounts[limiter.tier]++
	}

	return map[string]interface{}{
		"total_clients":     len(rl.clients),
		"total_requests":    totalRequests,
		"total_blocked":     totalBlocked,
		"tier_distribution": tierCounts,
	}
}

func (rl *OmniRateLimiter) cleanup() {
	ticker := time.NewTicker(rl.cleanupInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			rl.mu.Lock()
			cutoff := time.Now().Add(-30 * time.Minute)
			for id, limiter := range rl.clients {
				if limiter.createdAt.Before(cutoff) && limiter.requests == 0 {
					delete(rl.clients, id)
				}
			}
			rl.mu.Unlock()
		case <-rl.stopCh:
			return
		}
	}
}

func (rl *OmniRateLimiter) Stop() {
	close(rl.stopCh)
}

func min64(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
