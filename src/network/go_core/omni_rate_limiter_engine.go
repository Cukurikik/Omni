// ===========================================================================
// OMNI RATE LIMITER ENGINE (SEMESTER 3 — BATCH 38.5)
// ===========================================================================
// Absorbed From  : golang.org/x/time/rate + uber-go/ratelimit + leaky bucket
// Logic Inherited: Go / Network Layer (Token Bucket + Sliding Window)
// ===========================================================================

package network_gocore

import (
	"sync"
	"sync/atomic"
	"time"
)

// Result represents the outcome of a rate limit check.
type RateLimiterResult struct {
	Allowed    bool
	Remaining  int64
	RetryAfter time.Duration
	Limit      int64
	Window     time.Duration
}

// ---- Token Bucket Algorithm ----
// Tokens are added at a fixed rate. Each request consumes a token.
// If no tokens available, request is rejected.

type TokenBucket struct {
	rate       float64 // tokens per second
	maxTokens  float64 // bucket capacity
	tokens     float64 // current tokens
	lastRefill time.Time
	mu         sync.Mutex

	totalAllowed atomic.Uint64
	totalDenied  atomic.Uint64
}

func NewTokenBucket(ratePerSecond float64, burst int) *TokenBucket {
	return &TokenBucket{
		rate:       ratePerSecond,
		maxTokens:  float64(burst),
		tokens:     float64(burst),
		lastRefill: time.Now(),
	}
}

func (tb *TokenBucket) Allow() RateLimiterResult {
	return tb.AllowN(1)
}

func (tb *TokenBucket) AllowN(n int) RateLimiterResult {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()
	tb.lastRefill = now

	// Refill tokens
	tb.tokens += elapsed * tb.rate
	if tb.tokens > tb.maxTokens {
		tb.tokens = tb.maxTokens
	}

	requested := float64(n)
	if tb.tokens >= requested {
		tb.tokens -= requested
		tb.totalAllowed.Add(uint64(n))
		return RateLimiterResult{
			Allowed:   true,
			Remaining: int64(tb.tokens),
			Limit:     int64(tb.maxTokens),
		}
	}

	// Calculate retry after
	deficit := requested - tb.tokens
	retryAfter := time.Duration(deficit / tb.rate * float64(time.Second))

	tb.totalDenied.Add(uint64(n))
	return RateLimiterResult{
		Allowed:    false,
		Remaining:  0,
		RetryAfter: retryAfter,
		Limit:      int64(tb.maxTokens),
	}
}

// ---- Sliding Window Counter ----
// Counts requests in a sliding time window.

type SlidingWindow struct {
	windowSize  time.Duration
	maxRequests int64
	slots       []windowSlot
	slotCount   int
	mu          sync.Mutex

	totalAllowed atomic.Uint64
	totalDenied  atomic.Uint64
}

type windowSlot struct {
	timestamp time.Time
	count     int64
}

func NewSlidingWindow(windowSize time.Duration, maxRequests int64) *SlidingWindow {
	return &SlidingWindow{
		windowSize:  windowSize,
		maxRequests: maxRequests,
		slots:       make([]windowSlot, 0, 1000),
		slotCount:   0,
	}
}

func (sw *SlidingWindow) Allow() RateLimiterResult {
	sw.mu.Lock()
	defer sw.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-sw.windowSize)

	// Evict expired slots
	validStart := 0
	for i, slot := range sw.slots {
		if slot.timestamp.After(windowStart) {
			validStart = i
			break
		}
		if i == len(sw.slots)-1 {
			validStart = len(sw.slots)
		}
	}
	sw.slots = sw.slots[validStart:]

	// Count requests in window
	var count int64
	for _, slot := range sw.slots {
		count += slot.count
	}

	if count < sw.maxRequests {
		sw.slots = append(sw.slots, windowSlot{timestamp: now, count: 1})
		sw.totalAllowed.Add(1)
		return RateLimiterResult{
			Allowed:   true,
			Remaining: sw.maxRequests - count - 1,
			Limit:     sw.maxRequests,
			Window:    sw.windowSize,
		}
	}

	// Calculate retry delay
	var retryAfter time.Duration
	if len(sw.slots) > 0 {
		oldest := sw.slots[0].timestamp
		retryAfter = oldest.Add(sw.windowSize).Sub(now)
	}

	sw.totalDenied.Add(1)
	return RateLimiterResult{
		Allowed:    false,
		Remaining:  0,
		RetryAfter: retryAfter,
		Limit:      sw.maxRequests,
		Window:     sw.windowSize,
	}
}

// ---- Per-Key Rate Limiter ----
// Manages separate rate limits per key (e.g., per IP, per user).

type PerKeyLimiter struct {
	factory   func() *TokenBucket
	buckets   sync.Map // key -> *TokenBucket
	totalKeys atomic.Int64
}

func NewPerKeyLimiter(ratePerSecond float64, burst int) *PerKeyLimiter {
	return &PerKeyLimiter{
		factory: func() *TokenBucket {
			return NewTokenBucket(ratePerSecond, burst)
		},
	}
}

func (pkl *PerKeyLimiter) Allow(key string) RateLimiterResult {
	bucket, loaded := pkl.buckets.LoadOrStore(key, pkl.factory())
	if !loaded {
		pkl.totalKeys.Add(1)
	}
	return bucket.(*TokenBucket).Allow()
}

func (pkl *PerKeyLimiter) KeyCount() int64 {
	return pkl.totalKeys.Load()
}

// ---- Engine Facade ----

type OmniRateLimiterEngine struct {
	tokenBuckets   map[string]*TokenBucket
	slidingWindows map[string]*SlidingWindow
	perKeyLimiters map[string]*PerKeyLimiter
	mu             sync.RWMutex
}

func NewRateLimiterEngine() *OmniRateLimiterEngine {
	return &OmniRateLimiterEngine{
		tokenBuckets:   make(map[string]*TokenBucket),
		slidingWindows: make(map[string]*SlidingWindow),
		perKeyLimiters: make(map[string]*PerKeyLimiter),
	}
}

func (e *OmniRateLimiterEngine) CreateTokenBucket(name string, rps float64, burst int) *TokenBucket {
	e.mu.Lock()
	defer e.mu.Unlock()
	tb := NewTokenBucket(rps, burst)
	e.tokenBuckets[name] = tb
	return tb
}

func (e *OmniRateLimiterEngine) CreateSlidingWindow(name string, window time.Duration, max int64) *SlidingWindow {
	e.mu.Lock()
	defer e.mu.Unlock()
	sw := NewSlidingWindow(window, max)
	e.slidingWindows[name] = sw
	return sw
}

func (e *OmniRateLimiterEngine) CreatePerKeyLimiter(name string, rps float64, burst int) *PerKeyLimiter {
	e.mu.Lock()
	defer e.mu.Unlock()
	pkl := NewPerKeyLimiter(rps, burst)
	e.perKeyLimiters[name] = pkl
	return pkl
}

func (e *OmniRateLimiterEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":           "OmniRateLimiterEngine",
		"layer":            "Go Network",
		"token_buckets":    len(e.tokenBuckets),
		"sliding_windows":  len(e.slidingWindows),
		"per_key_limiters": len(e.perKeyLimiters),
		"learned_logic": []string{
			"token-bucket-algorithm",
			"sliding-window-counter",
			"per-key-sync-map-limiter",
			"mutex-protected-refill",
			"retry-after-calculation",
			"slot-eviction-expired",
			"load-or-store-atomic",
			"rwmutex-reader-writer",
		},
	}
}

