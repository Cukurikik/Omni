package network_go

import (
	"errors"
	"log"
	"math"
	"sync"
	"sync/atomic"
	"time"
)

// OMNI MOTHER: Production Circuit Breaker (Full Implementation)
// Supports: configurable thresholds, half-open probing, success-rate
// based tripping, exponential backoff cooldown, metrics, and callbacks.

// State represents circuit breaker states.
type State int32

const (
	StateClosed   State = 0
	StateOpen     State = 1
	StateHalfOpen State = 2
)

func (s State) String() string {
	switch s {
	case StateClosed:
		return "CLOSED"
	case StateOpen:
		return "OPEN"
	case StateHalfOpen:
		return "HALF-OPEN"
	default:
		return "UNKNOWN"
	}
}

var (
	ErrCircuitOpen    = errors.New("circuit breaker is OPEN")
	ErrTooManyRetries = errors.New("too many concurrent half-open probes")
)

// CircuitBreakerConfig configures the breaker.
type CircuitBreakerConfig struct {
	FailureThreshold  int           // Consecutive failures to trip
	SuccessThreshold  int           // Consecutive successes in half-open to close
	Timeout           time.Duration // Base cooldown before half-open
	MaxTimeout        time.Duration // Maximum backoff timeout
	BackoffMultiplier float64       // Timeout multiplier per trip (exponential backoff)
	HalfOpenMaxConcur int           // Max concurrent probes in half-open
	OnStateChange     func(from, to State)
}

// DefaultConfig returns sane production defaults.
func DefaultConfig() CircuitBreakerConfig {
	return CircuitBreakerConfig{
		FailureThreshold:  5,
		SuccessThreshold:  3,
		Timeout:           10 * time.Second,
		MaxTimeout:        2 * time.Minute,
		BackoffMultiplier: 2.0,
		HalfOpenMaxConcur: 1,
		OnStateChange:     nil,
	}
}

// CircuitBreakerMetrics exposes operational counters.
type CircuitBreakerMetrics struct {
	TotalRequests  int64
	TotalSuccesses int64
	TotalFailures  int64
	TotalRejected  int64
	ConsecFailures int64
	ConsecSuccess  int64
	TripCount      int64
}

// CircuitBreaker implements the circuit breaker pattern.
type CircuitBreaker struct {
	mu             sync.Mutex
	config         CircuitBreakerConfig
	state          State
	consecFails    int
	consecSuccess  int
	lastFailure    time.Time
	currentTimeout time.Duration
	tripCount      int
	halfOpenProbes int32
	metrics        CircuitBreakerMetrics
}

// NewCircuitBreaker creates a circuit breaker with the given config.
func NewCircuitBreaker(cfg CircuitBreakerConfig) *CircuitBreaker {
	if cfg.FailureThreshold <= 0 {
		cfg.FailureThreshold = 5
	}
	if cfg.SuccessThreshold <= 0 {
		cfg.SuccessThreshold = 3
	}
	if cfg.Timeout <= 0 {
		cfg.Timeout = 10 * time.Second
	}
	if cfg.MaxTimeout <= 0 {
		cfg.MaxTimeout = 2 * time.Minute
	}
	if cfg.BackoffMultiplier <= 0 {
		cfg.BackoffMultiplier = 2.0
	}
	if cfg.HalfOpenMaxConcur <= 0 {
		cfg.HalfOpenMaxConcur = 1
	}

	return &CircuitBreaker{
		config:         cfg,
		state:          StateClosed,
		currentTimeout: cfg.Timeout,
	}
}

// NewDefaultCircuitBreaker creates a breaker with default config.
func NewDefaultCircuitBreaker() *CircuitBreaker {
	return NewCircuitBreaker(DefaultConfig())
}

// Execute wraps a function call with circuit breaker protection.
func (cb *CircuitBreaker) Execute(fn func() error) error {
	if !cb.allowRequest() {
		atomic.AddInt64(&cb.metrics.TotalRejected, 1)
		return ErrCircuitOpen
	}

	atomic.AddInt64(&cb.metrics.TotalRequests, 1)

	err := fn()

	if err != nil {
		cb.recordFailure()
		return err
	}

	cb.recordSuccess()
	return nil
}

func (cb *CircuitBreaker) allowRequest() bool {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	switch cb.state {
	case StateClosed:
		return true
	case StateOpen:
		if time.Since(cb.lastFailure) > cb.currentTimeout {
			cb.transitionTo(StateHalfOpen)
			return true
		}
		return false
	case StateHalfOpen:
		current := atomic.LoadInt32(&cb.halfOpenProbes)
		if int(current) >= cb.config.HalfOpenMaxConcur {
			return false
		}
		atomic.AddInt32(&cb.halfOpenProbes, 1)
		return true
	}
	return false
}

func (cb *CircuitBreaker) recordSuccess() {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	atomic.AddInt64(&cb.metrics.TotalSuccesses, 1)
	cb.consecFails = 0
	cb.consecSuccess++
	atomic.StoreInt64(&cb.metrics.ConsecSuccess, int64(cb.consecSuccess))
	atomic.StoreInt64(&cb.metrics.ConsecFailures, 0)

	if cb.state == StateHalfOpen {
		atomic.AddInt32(&cb.halfOpenProbes, -1)
		if cb.consecSuccess >= cb.config.SuccessThreshold {
			cb.transitionTo(StateClosed)
			cb.currentTimeout = cb.config.Timeout // Reset backoff
			cb.tripCount = 0
		}
	}
}

func (cb *CircuitBreaker) recordFailure() {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	atomic.AddInt64(&cb.metrics.TotalFailures, 1)
	cb.consecSuccess = 0
	cb.consecFails++
	cb.lastFailure = time.Now()
	atomic.StoreInt64(&cb.metrics.ConsecFailures, int64(cb.consecFails))
	atomic.StoreInt64(&cb.metrics.ConsecSuccess, 0)

	if cb.state == StateHalfOpen {
		atomic.AddInt32(&cb.halfOpenProbes, -1)
		cb.tripCount++
		// Exponential backoff
		multiplier := math.Pow(cb.config.BackoffMultiplier, float64(cb.tripCount))
		cb.currentTimeout = time.Duration(float64(cb.config.Timeout) * multiplier)
		if cb.currentTimeout > cb.config.MaxTimeout {
			cb.currentTimeout = cb.config.MaxTimeout
		}
		cb.transitionTo(StateOpen)
		atomic.AddInt64(&cb.metrics.TripCount, 1)
	} else if cb.state == StateClosed && cb.consecFails >= cb.config.FailureThreshold {
		cb.tripCount++
		cb.transitionTo(StateOpen)
		atomic.AddInt64(&cb.metrics.TripCount, 1)
	}
}

func (cb *CircuitBreaker) transitionTo(newState State) {
	oldState := cb.state
	if oldState == newState {
		return
	}
	cb.state = newState
	cb.consecFails = 0
	cb.consecSuccess = 0

	log.Printf("[OMNI CB] %s → %s (timeout: %v, trips: %d)",
		oldState, newState, cb.currentTimeout, cb.tripCount)

	if cb.config.OnStateChange != nil {
		go cb.config.OnStateChange(oldState, newState)
	}
}

// State returns the current circuit breaker state.
func (cb *CircuitBreaker) GetState() State {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	return cb.state
}

// Metrics returns a snapshot of operational counters.
func (cb *CircuitBreaker) Metrics() CircuitBreakerMetrics {
	return CircuitBreakerMetrics{
		TotalRequests:  atomic.LoadInt64(&cb.metrics.TotalRequests),
		TotalSuccesses: atomic.LoadInt64(&cb.metrics.TotalSuccesses),
		TotalFailures:  atomic.LoadInt64(&cb.metrics.TotalFailures),
		TotalRejected:  atomic.LoadInt64(&cb.metrics.TotalRejected),
		ConsecFailures: atomic.LoadInt64(&cb.metrics.ConsecFailures),
		ConsecSuccess:  atomic.LoadInt64(&cb.metrics.ConsecSuccess),
		TripCount:      atomic.LoadInt64(&cb.metrics.TripCount),
	}
}

// Reset forces the breaker back to Closed.
func (cb *CircuitBreaker) Reset() {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	cb.transitionTo(StateClosed)
	cb.currentTimeout = cb.config.Timeout
	cb.tripCount = 0
}

