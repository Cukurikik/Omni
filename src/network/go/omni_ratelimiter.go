package network_go

import (
	"net/http"
	"sync"
	"time"
)

// OMNI MOTHER: Token Bucket Rate Limiter Middleware (Production Grade)

type Visitor struct {
	tokens int
	last   time.Time
}

type RateLimiter struct {
	visitors map[string]*Visitor
	mu       sync.Mutex
	rate     int
	burst    int
}

func NewRateLimiter(rate int, burst int) *RateLimiter {
	return &RateLimiter{
		visitors: make(map[string]*Visitor),
		rate:     rate,
		burst:    burst,
	}
}

func (rl *RateLimiter) Limit(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ip := r.RemoteAddr

		rl.mu.Lock()
		v, exists := rl.visitors[ip]
		if !exists {
			rl.visitors[ip] = &Visitor{tokens: rl.burst, last: time.Now()}
			v = rl.visitors[ip]
		}

		now := time.Now()
		elapsed := now.Sub(v.last).Seconds()
		v.tokens += int(elapsed * float64(rl.rate))
		if v.tokens > rl.burst {
			v.tokens = rl.burst
		}

		if v.tokens > 0 {
			v.tokens--
			v.last = now
			rl.mu.Unlock()
			next.ServeHTTP(w, r)
		} else {
			rl.mu.Unlock()
			http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
		}
	})
}

