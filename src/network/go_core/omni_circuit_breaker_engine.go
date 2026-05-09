// ===========================================================================
// OMNI CIRCUIT BREAKER ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : Sony gobreaker + Hystrix-go + resilience4j patterns
// Logic Inherited: Go / Network Layer (Resilience & Fault Tolerance)
// ===========================================================================
//
// By studying gobreaker and resilience patterns, Mother learned:
//   1. Circuit Breaker states: Closed → Open → Half-Open
//   2. Closed: normal operation, errors counted toward threshold
//   3. Open: all calls fail-fast, timer starts for recovery attempt
//   4. Half-Open: limited probing calls to test if service recovered
//   5. Retry with exponential backoff prevents thundering herd

package network_gocore

import (
	"context"
	"errors"
	"fmt"
	"math"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// ============================================================
// PART 1: Circuit Breaker
// ============================================================

// State represents the circuit breaker state.
type CBState int32

const (
	CBStateClosed   CBState = iota // Normal operation
	CBStateOpen                    // Failing fast
	CBStateHalfOpen                // Probing for recovery
)

func (s CBState) String() string {
	switch s {
	case CBStateClosed:
		return "CLOSED"
	case CBStateOpen:
		return "OPEN"
	case CBStateHalfOpen:
		return "HALF_OPEN"
	default:
		return "UNKNOWN"
	}
}

// CircuitBreakerConfig holds configuration parameters.
type CircuitBreakerConfig struct {
	MaxFailures      int           // Failures before opening
	Timeout          time.Duration // How long to stay open before half-open
	HalfOpenMaxCalls int           // Max probe calls in half-open
	SuccessThreshold int           // Successes needed to close from half-open
	OnStateChange    func(from, to CBState)
}

// DefaultCircuitBreakerConfig returns sensible defaults.
func DefaultCircuitBreakerConfig() CircuitBreakerConfig {
	return CircuitBreakerConfig{
		MaxFailures:      5,
		Timeout:          30 * time.Second,
		HalfOpenMaxCalls: 3,
		SuccessThreshold: 2,
	}
}

// CircuitBreaker implements the circuit breaker pattern.
type CircuitBreaker struct {
	name   string
	config CircuitBreakerConfig
	mu     sync.Mutex
	state  CBState

	// Counters
	failures      int
	successes     int
	halfOpenCalls int
	lastFailure   time.Time

	// Metrics
	totalCalls     int64
	totalSuccesses int64
	totalFailures  int64
	totalRejected  int64
}

// NewCBEngine creates a new circuit breaker.
func NewCBEngine(name string, config CircuitBreakerConfig) *CircuitBreaker {
	return &CircuitBreaker{
		name:   name,
		config: config,
		state:  CBStateClosed,
	}
}

var (
	ErrCircuitOpen  = errors.New("circuit breaker is open")
	ErrTooManyCalls = errors.New("too many calls in half-open state")
)

// Execute runs the given function through the circuit breaker.
func (cb *CircuitBreaker) Execute(fn func() (interface{}, error)) (interface{}, error) {
	atomic.AddInt64(&cb.totalCalls, 1)

	if err := cb.allowRequest(); err != nil {
		atomic.AddInt64(&cb.totalRejected, 1)
		return nil, err
	}

	result, err := fn()

	if err != nil {
		cb.recordFailure()
		return nil, err
	}

	cb.recordSuccess()
	return result, nil
}

// ExecuteWithContext adds context-based cancellation.
func (cb *CircuitBreaker) ExecuteWithContext(
	ctx context.Context,
	fn func(ctx context.Context) (interface{}, error),
) (interface{}, error) {
	atomic.AddInt64(&cb.totalCalls, 1)

	if err := cb.allowRequest(); err != nil {
		atomic.AddInt64(&cb.totalRejected, 1)
		return nil, err
	}

	resultCh := make(chan struct {
		result interface{}
		err    error
	}, 1)

	go func() {
		result, err := fn(ctx)
		resultCh <- struct {
			result interface{}
			err    error
		}{result, err}
	}()

	select {
	case <-ctx.Done():
		cb.recordFailure()
		return nil, ctx.Err()
	case r := <-resultCh:
		if r.err != nil {
			cb.recordFailure()
			return nil, r.err
		}
		cb.recordSuccess()
		return r.result, nil
	}
}

func (cb *CircuitBreaker) allowRequest() error {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	switch cb.state {
	case CBStateClosed:
		return nil

	case CBStateOpen:
		// Check if timeout has elapsed
		if time.Since(cb.lastFailure) > cb.config.Timeout {
			cb.transitionTo(CBStateHalfOpen)
			cb.halfOpenCalls = 1
			return nil
		}
		return ErrCircuitOpen

	case CBStateHalfOpen:
		if cb.halfOpenCalls >= cb.config.HalfOpenMaxCalls {
			return ErrTooManyCalls
		}
		cb.halfOpenCalls++
		return nil
	}

	return nil
}

func (cb *CircuitBreaker) recordSuccess() {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	atomic.AddInt64(&cb.totalSuccesses, 1)

	switch cb.state {
	case CBStateClosed:
		cb.failures = 0 // Reset failure count on success

	case CBStateHalfOpen:
		cb.successes++
		if cb.successes >= cb.config.SuccessThreshold {
			cb.transitionTo(CBStateClosed)
			cb.reset()
		}
	}
}

func (cb *CircuitBreaker) recordFailure() {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	atomic.AddInt64(&cb.totalFailures, 1)
	cb.lastFailure = time.Now()

	switch cb.state {
	case CBStateClosed:
		cb.failures++
		if cb.failures >= cb.config.MaxFailures {
			cb.transitionTo(CBStateOpen)
		}

	case CBStateHalfOpen:
		cb.transitionTo(CBStateOpen)
	}
}

func (cb *CircuitBreaker) transitionTo(newState CBState) {
	oldState := cb.state
	cb.state = newState
	if cb.config.OnStateChange != nil {
		go cb.config.OnStateChange(oldState, newState)
	}
}

func (cb *CircuitBreaker) reset() {
	cb.failures = 0
	cb.successes = 0
	cb.halfOpenCalls = 0
}

// GetState returns the current state.
func (cb *CircuitBreaker) GetState() CBState {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	return cb.state
}

// ============================================================
// PART 2: Retry with Backoff
// ============================================================

// RetryConfig configures retry behavior.
type RetryConfig struct {
	MaxRetries  int
	InitialWait time.Duration
	MaxWait     time.Duration
	Factor      float64 // Backoff multiplier
	Jitter      bool    // Add random jitter
}

// DefaultRetryConfig returns sensible defaults.
func DefaultRetryConfig() RetryConfig {
	return RetryConfig{
		MaxRetries:  3,
		InitialWait: 100 * time.Millisecond,
		MaxWait:     10 * time.Second,
		Factor:      2.0,
		Jitter:      true,
	}
}

// Retry executes a function with exponential backoff.
func Retry(ctx context.Context, config RetryConfig, fn func(attempt int) error) error {
	var lastErr error

	for attempt := 0; attempt <= config.MaxRetries; attempt++ {
		if err := ctx.Err(); err != nil {
			return fmt.Errorf("context cancelled during retry: %w", err)
		}

		lastErr = fn(attempt)
		if lastErr == nil {
			return nil
		}

		if attempt < config.MaxRetries {
			wait := calculateBackoff(attempt, config)
			select {
			case <-time.After(wait):
			case <-ctx.Done():
				return ctx.Err()
			}
		}
	}

	return fmt.Errorf("all %d retries exhausted: %w", config.MaxRetries, lastErr)
}

func calculateBackoff(attempt int, config RetryConfig) time.Duration {
	wait := time.Duration(float64(config.InitialWait) * math.Pow(config.Factor, float64(attempt)))
	if wait > config.MaxWait {
		wait = config.MaxWait
	}
	if config.Jitter {
		jitter := time.Duration(rand.Int63n(int64(wait) / 2))
		wait = wait/2 + jitter
	}
	return wait
}

// ============================================================
// PART 3: Bulkhead (Concurrent Call Limiter)
// ============================================================

// Bulkhead limits the number of concurrent calls to a resource.
type Bulkhead struct {
	name        string
	sem         chan struct{}
	maxConcur   int
	totalCalls  int64
	totalReject int64
}

// NewBulkhead creates a bulkhead with the given concurrency limit.
func NewBulkhead(name string, maxConcurrency int) *Bulkhead {
	return &Bulkhead{
		name:      name,
		sem:       make(chan struct{}, maxConcurrency),
		maxConcur: maxConcurrency,
	}
}

// Execute runs the function within the bulkhead.
func (b *Bulkhead) Execute(ctx context.Context, fn func() (interface{}, error)) (interface{}, error) {
	atomic.AddInt64(&b.totalCalls, 1)

	select {
	case b.sem <- struct{}{}:
		defer func() { <-b.sem }()
		return fn()
	case <-ctx.Done():
		atomic.AddInt64(&b.totalReject, 1)
		return nil, ctx.Err()
	}
}

// TryExecute attempts to run without blocking.
func (b *Bulkhead) TryExecute(fn func() (interface{}, error)) (interface{}, error) {
	select {
	case b.sem <- struct{}{}:
		defer func() { <-b.sem }()
		return fn()
	default:
		atomic.AddInt64(&b.totalReject, 1)
		return nil, fmt.Errorf("bulkhead %s: max concurrency reached", b.name)
	}
}

// ============================================================
// Diagnostics
// ============================================================

func (cb *CircuitBreaker) Diagnostics() map[string]interface{} {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	return map[string]interface{}{
		"engine":         "OmniCircuitBreakerEngine",
		"layer":          "Go Network",
		"name":           cb.name,
		"state":          cb.state.String(),
		"failures":       cb.failures,
		"maxFailures":    cb.config.MaxFailures,
		"totalCalls":     atomic.LoadInt64(&cb.totalCalls),
		"totalSuccesses": atomic.LoadInt64(&cb.totalSuccesses),
		"totalFailures":  atomic.LoadInt64(&cb.totalFailures),
		"totalRejected":  atomic.LoadInt64(&cb.totalRejected),
		"learned_logic": []string{
			"circuit-breaker-three-states",
			"closed-open-halfopen-transitions",
			"timeout-recovery-probe",
			"retry-exponential-backoff-jitter",
			"bulkhead-concurrent-call-limit",
			"context-cancellation-propagation",
			"atomic-counter-lock-free-metrics",
			"fail-fast-resource-protection",
		},
	}
}

