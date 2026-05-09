package grpc

// omni_grpc_ratelimiter.go — Token Bucket Rate Limiter
// Layer: Network / Security
// Inspired by: golang.org/x/time/rate
//
// Implements a gRPC Unary Interceptor using a standard Token Bucket algorithm.
// Protects backend services from Denial-of-Service by limiting requests per IP
// or Client ID. Uses standard Go mutexes for thread safety. Zero mock.

import (
	"context"
	"sync"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/peer"
	"google.golang.org/grpc/status"
)

type TokenBucket struct {
	mu           sync.Mutex
	tokens       float64
	capacity     float64
	refillRate   float64 // tokens per second
	lastRefilled time.Time
}

func NewTokenBucket(capacity float64, refillRate float64) *TokenBucket {
	return &TokenBucket{
		tokens:       capacity,
		capacity:     capacity,
		refillRate:   refillRate,
		lastRefilled: time.Now(),
	}
}

func (tb *TokenBucket) Take() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(tb.lastRefilled).Seconds()

	// Refill tokens
	tb.tokens += elapsed * tb.refillRate
	if tb.tokens > tb.capacity {
		tb.tokens = tb.capacity
	}
	tb.lastRefilled = now

	// Check if token available
	if tb.tokens >= 1.0 {
		tb.tokens -= 1.0
		return true
	}

	return false
}

type OmniRateLimiter struct {
	mu         sync.RWMutex
	buckets    map[string]*TokenBucket
	capacity   float64
	refillRate float64
}

func NewOmniRateLimiter(capacity, refillRate float64) *OmniRateLimiter {
	return &OmniRateLimiter{
		buckets:    make(map[string]*TokenBucket),
		capacity:   capacity,
		refillRate: refillRate,
	}
}

func (rl *OmniRateLimiter) getBucket(clientIP string) *TokenBucket {
	rl.mu.RLock()
	bucket, exists := rl.buckets[clientIP]
	rl.mu.RUnlock()

	if exists {
		return bucket
	}

	// Create new bucket
	rl.mu.Lock()
	defer rl.mu.Unlock()
	// Double-check locking
	if bucket, exists = rl.buckets[clientIP]; exists {
		return bucket
	}

	bucket = NewTokenBucket(rl.capacity, rl.refillRate)
	rl.buckets[clientIP] = bucket
	return bucket
}

// UnaryInterceptor returns a gRPC interceptor that applies rate limiting
func (rl *OmniRateLimiter) UnaryInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {

		var clientIP string
		if p, ok := peer.FromContext(ctx); ok {
			clientIP = p.Addr.String()
		} else {
			clientIP = "unknown"
		}

		bucket := rl.getBucket(clientIP)

		if !bucket.Take() {
			return nil, status.Errorf(codes.ResourceExhausted, "OMNI gRPC: Rate limit exceeded for %s", clientIP)
		}

		return handler(ctx, req)
	}
}

