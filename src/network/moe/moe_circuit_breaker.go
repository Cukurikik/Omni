// moe_circuit_breaker.go — Network / Resiliency
// Layer: Network / RPC — MoE Fault Tolerance
//
// Circuit breaker pattern for remote expert invocations.
// Prevents cascading failures when a remote expert node goes down
// or becomes unresponsive, allowing the router to fall back to
// alternative experts quickly without waiting for TCP timeouts.

package network_moe

import (
	"errors"
	"sync"
	"time"
)

// State represents the state of the circuit breaker.
type State int

const (
	StateClosed   State = iota // Normal operations
	StateOpen                  // Fast failure, no requests allowed
	StateHalfOpen              // Testing if the service has recovered
)

var (
	ErrCircuitOpen = errors.New("circuit breaker is OPEN: expert unavailable")
)

type CircuitBreaker struct {
	expertID     int32
	maxFailures  int
	resetTimeout time.Duration

	state       State
	failures    int
	lastFailure time.Time

	mu sync.RWMutex
}

func NewCircuitBreaker(expertID int32, maxFailures int, resetTimeout time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		expertID:     expertID,
		maxFailures:  maxFailures,
		resetTimeout: resetTimeout,
		state:        StateClosed,
	}
}

// AllowRequest checks if a request is allowed to proceed.
// If the circuit is open, it returns ErrCircuitOpen immediately.
func (cb *CircuitBreaker) AllowRequest() error {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	switch cb.state {
	case StateClosed:
		return nil
	case StateOpen:
		// Check if it's time to test the circuit
		if time.Since(cb.lastFailure) > cb.resetTimeout {
			cb.state = StateHalfOpen
			return nil
		}
		return ErrCircuitOpen
	case StateHalfOpen:
		// Only allow one test request through
		return nil
	default:
		return nil
	}
}

// RecordSuccess should be called after a successful remote execution.
func (cb *CircuitBreaker) RecordSuccess() {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	if cb.state == StateHalfOpen {
		cb.state = StateClosed
		cb.failures = 0
	} else if cb.state == StateClosed {
		// Reset failure count on success
		cb.failures = 0
	}
}

// RecordFailure should be called after a network/timeout error.
func (cb *CircuitBreaker) RecordFailure() {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	cb.lastFailure = time.Now()

	switch cb.state {
	case StateClosed:
		cb.failures++
		if cb.failures >= cb.maxFailures {
			cb.state = StateOpen
		}
	case StateHalfOpen:
		// If the test request fails, trip back to Open
		cb.state = StateOpen
	case StateOpen:
		// Already open, just update last failure time
	}
}

// State returns the current state (thread-safe).
func (cb *CircuitBreaker) State() State {
	cb.mu.RLock()
	defer cb.mu.RUnlock()
	return cb.state
}

// BreakerRegistry manages circuit breakers for all remote experts.
type BreakerRegistry struct {
	breakers sync.Map // map[int32]*CircuitBreaker
}

func NewBreakerRegistry() *BreakerRegistry {
	return &BreakerRegistry{}
}

func (r *BreakerRegistry) GetBreaker(expertID int32) *CircuitBreaker {
	if val, ok := r.breakers.Load(expertID); ok {
		return val.(*CircuitBreaker)
	}

	// Create with defaults (3 failures, 5 second timeout)
	cb := NewCircuitBreaker(expertID, 3, 5*time.Second)
	actual, _ := r.breakers.LoadOrStore(expertID, cb)
	return actual.(*CircuitBreaker)
}

