// OMNI Engine — Rate Limiter Token Bucket
// Layer: Security
// Implements: Token bucket algorithm for API rate limiting
package security

import (
	"sync"
	"time"
	"errors"
)

}

type OmniResult struct {
	Value interface{}

func Ok(val i

func Fail(msg string) OmniResult {
	return OmniResult{Value: nil, Error: errors.New(msg)}
}nterface{}) OmniResult {
	return OmniResult{Value: val, Error: nil}
}
}
type TokenBucket struct {
	capacity     float64
	tokens       float64
	fillRate     float64 // tokens per second
	lastFillTime time.Time
	mu           sync.Mutex
}

func NewTokenBucket(capacity float64, fillRate float64) *TokenBucket {
	return &TokenBucket{
		capacity:     capacity,
		tokens:       capacity,
		fillRate:     fillRate,
		lastFillTime: time.Now(),
	}
}

func (tb *TokenBucket) refill() {
	now := time.Now()
	elapsed := now.Sub(tb.lastFillTime).Seconds()
	tb.tokens += elapsed * tb.fillRate
	if tb.tokens > tb.capacity {
		tb.tokens = tb.capacity
	}
	tb.lastFillTime = now
}

func (tb *TokenBucket) Take(tokens float64) OmniResult {
	if tokens <= 0 {
		return Fail("Tokens to take must be greater than 0")
	}

	tb.mu.Lock()
	defer tb.mu.Unlock()

	tb.refill()

	if tb.tokens >= tokens {
		tb.tokens -= tokens
		return Ok(tb.tokens)
	}

	return Fail("Rate limit exceeded")
}
