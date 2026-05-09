// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// OMNI CIRCUIT BREAKER ENGINE — Fault-Tolerant Service Protection (Network Layer)
// Production-grade circuit breaker with half-open probing, exponential backoff,
// sliding window metrics, and health-based auto-recovery.
// Layer: NETWORK (Go)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

package network_gocore

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
	"time"
)

// ── Monadic Result Type ─────────────────────────────────────────────────────────

// Result represents a monadic operation result for OMNI compliance.
type Result[T any] struct {
	Value T
	Err   error
	IsOk  bool
}

// Ok creates a successful Result.
func Ok[T any](val T) Result[T] {
	return Result[T]{Value: val, IsOk: true}
}

// Err creates an error Result.
func Err[T any](err error) Result[T] {
	return Result[T]{Err: err, IsOk: false}
}

// ── Circuit Breaker State ───────────────────────────────────────────────────────

// CircuitState represents the circuit breaker state.
type CircuitState int32

const (
	StateClosed   CircuitState = 0 // Normal operation — requests pass through
	StateOpen     CircuitState = 1 // Circuit tripped — requests rejected
	StateHalfOpen CircuitState = 2 // Testing recovery — limited requests pass
)

func (s CircuitState) String() string {
	switch s {
	case StateClosed:
		return "CLOSED"
	case StateOpen:
		return "OPEN"
	case StateHalfOpen:
		return "HALF_OPEN"
	default:
		return "UNKNOWN"
	}
}

// ── Sliding Window Metrics ──────────────────────────────────────────────────────

// SlidingWindowMetrics tracks success/failure counts in a time-based sliding window.
type SlidingWindowMetrics struct {
	mu          sync.RWMutex
	windowSize  time.Duration
	bucketSize  time.Duration
	buckets     []bucket
	numBuckets  int
	headIdx     int
	lastRotated time.Time
}

type bucket struct {
	successes int64
	failures  int64
	timeouts  int64
	rejects   int64
}

// NewSlidingWindowMetrics creates a new sliding window with the given parameters.
func NewSlidingWindowMetrics(windowSize time.Duration, numBuckets int) *SlidingWindowMetrics {
	if numBuckets < 1 {
		numBuckets = 10
	}
	bucketSize := windowSize / time.Duration(numBuckets)
	return &SlidingWindowMetrics{
		windowSize:  windowSize,
		bucketSize:  bucketSize,
		buckets:     make([]bucket, numBuckets),
		numBuckets:  numBuckets,
		headIdx:     0,
		lastRotated: time.Now(),
	}
}

// rotate advances buckets based on elapsed time.
func (sw *SlidingWindowMetrics) rotate() {
	now := time.Now()
	elapsed := now.Sub(sw.lastRotated)
	bucketsToRotate := int(elapsed / sw.bucketSize)

	if bucketsToRotate <= 0 {
		return
	}

	if bucketsToRotate > sw.numBuckets {
		bucketsToRotate = sw.numBuckets
	}

	for i := 0; i < bucketsToRotate; i++ {
		sw.headIdx = (sw.headIdx + 1) % sw.numBuckets
		sw.buckets[sw.headIdx] = bucket{} // clear
	}
	sw.lastRotated = now
}

// RecordSuccess records a successful operation.
func (sw *SlidingWindowMetrics) RecordSuccess() {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	sw.rotate()
	sw.buckets[sw.headIdx].successes++
}

// RecordFailure records a failed operation.
func (sw *SlidingWindowMetrics) RecordFailure() {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	sw.rotate()
	sw.buckets[sw.headIdx].failures++
}

// RecordTimeout records a timed-out operation.
func (sw *SlidingWindowMetrics) RecordTimeout() {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	sw.rotate()
	sw.buckets[sw.headIdx].timeouts++
}

// RecordReject records a rejected operation (circuit open).
func (sw *SlidingWindowMetrics) RecordReject() {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	sw.rotate()
	sw.buckets[sw.headIdx].rejects++
}

// Summary returns aggregate metrics across the window.
func (sw *SlidingWindowMetrics) Summary() MetricsSummary {
	sw.mu.RLock()
	defer sw.mu.RUnlock()

	var total MetricsSummary
	for _, b := range sw.buckets {
		total.Successes += b.successes
		total.Failures += b.failures
		total.Timeouts += b.timeouts
		total.Rejects += b.rejects
	}

	totalOps := total.Successes + total.Failures + total.Timeouts
	if totalOps > 0 {
		total.ErrorRate = float64(total.Failures+total.Timeouts) / float64(totalOps)
	}
	total.TotalOps = totalOps

	return total
}

// Reset clears all metrics.
func (sw *SlidingWindowMetrics) Reset() {
	sw.mu.Lock()
	defer sw.mu.Unlock()
	for i := range sw.buckets {
		sw.buckets[i] = bucket{}
	}
}

// MetricsSummary provides an aggregate view of the sliding window.
type MetricsSummary struct {
	Successes int64   `json:"successes"`
	Failures  int64   `json:"failures"`
	Timeouts  int64   `json:"timeouts"`
	Rejects   int64   `json:"rejects"`
	TotalOps  int64   `json:"total_ops"`
	ErrorRate float64 `json:"error_rate"`
}

// ── Circuit Breaker Configuration ───────────────────────────────────────────────

// CBConfigLegacy holds the configuration for a circuit breaker.
type CBConfigLegacy struct {
	// Name identifies this circuit breaker instance.
	Name string

	// ErrorThreshold is the error rate (0.0-1.0) that triggers the circuit to open.
	ErrorThreshold float64

	// MinimumRequests is the minimum number of requests before evaluating the threshold.
	MinimumRequests int64

	// OpenDuration is how long the circuit stays open before transitioning to half-open.
	OpenDuration time.Duration

	// HalfOpenMaxRequests is the maximum concurrent requests allowed in half-open state.
	HalfOpenMaxRequests int32

	// WindowSize is the sliding window duration for metrics.
	WindowSize time.Duration

	// WindowBuckets is the number of buckets in the sliding window.
	WindowBuckets int

	// MaxConsecutiveFailures triggers open even if threshold not reached.
	MaxConsecutiveFailures int64

	// OnStateChange is called when state transitions occur.
	OnStateChange func(name string, from, to CircuitState)
}

// DefaultCBConfigLegacy returns a sensible default configuration.
func DefaultCBConfigLegacy(name string) CBConfigLegacy {
	return CBConfigLegacy{
		Name:                   name,
		ErrorThreshold:         0.5,
		MinimumRequests:        10,
		OpenDuration:           30 * time.Second,
		HalfOpenMaxRequests:    3,
		WindowSize:             60 * time.Second,
		WindowBuckets:          10,
		MaxConsecutiveFailures: 5,
	}
}

// ── OmniCircuitBreaker ──────────────────────────────────────────────────────────

// OmniCircuitBreaker implements a production-grade circuit breaker pattern.
type OmniCircuitBreaker struct {
	config CBConfigLegacy

	state             int32 // atomic CircuitState
	metrics           *SlidingWindowMetrics
	lastStateChange   time.Time
	consecutiveErrors int64 // atomic
	halfOpenPermits   int32 // atomic

	mu sync.RWMutex

	// Statistics
	totalTrips  int64 // atomic — total times circuit opened
	totalResets int64 // atomic — total times circuit closed from open
	createdAt   time.Time
}

const (
	EngineID = "OmniCircuitBreaker"
	Version  = "1.0.0-omni"
)

// NewCircuitBreaker creates a new circuit breaker with the given configuration.
func NewCircuitBreaker(config CBConfigLegacy) Result[*OmniCircuitBreaker] {
	if config.ErrorThreshold <= 0 || config.ErrorThreshold > 1.0 {
		return Err[*OmniCircuitBreaker](fmt.Errorf("error_threshold must be in (0.0, 1.0], got %f", config.ErrorThreshold))
	}
	if config.MinimumRequests < 1 {
		return Err[*OmniCircuitBreaker](fmt.Errorf("minimum_requests must be >= 1"))
	}
	if config.OpenDuration < time.Millisecond {
		return Err[*OmniCircuitBreaker](fmt.Errorf("open_duration must be >= 1ms"))
	}

	now := time.Now()
	cb := &OmniCircuitBreaker{
		config:          config,
		state:           int32(StateClosed),
		metrics:         NewSlidingWindowMetrics(config.WindowSize, config.WindowBuckets),
		lastStateChange: now,
		createdAt:       now,
	}

	return Ok(cb)
}

// State returns the current circuit state.
func (cb *OmniCircuitBreaker) State() CircuitState {
	return CircuitState(atomic.LoadInt32(&cb.state))
}

// Allow checks if a request is allowed through the circuit.
func (cb *OmniCircuitBreaker) Allow() Result[bool] {
	state := cb.State()

	switch state {
	case StateClosed:
		return Ok(true)

	case StateOpen:
		// Check if open duration has elapsed
		cb.mu.RLock()
		elapsed := time.Since(cb.lastStateChange)
		cb.mu.RUnlock()

		if elapsed >= cb.config.OpenDuration {
			cb.transitionTo(StateHalfOpen)
			return cb.Allow() // re-evaluate in half-open
		}

		cb.metrics.RecordReject()
		return Ok(false)

	case StateHalfOpen:
		// Limit concurrent requests in half-open
		current := atomic.AddInt32(&cb.halfOpenPermits, 1)
		if current > cb.config.HalfOpenMaxRequests {
			atomic.AddInt32(&cb.halfOpenPermits, -1)
			cb.metrics.RecordReject()
			return Ok(false)
		}
		return Ok(true)

	default:
		return Err[bool](fmt.Errorf("unknown circuit state: %d", state))
	}
}

// RecordSuccess records a successful operation and evaluates state.
func (cb *OmniCircuitBreaker) RecordSuccess() {
	cb.metrics.RecordSuccess()
	atomic.StoreInt64(&cb.consecutiveErrors, 0)

	if cb.State() == StateHalfOpen {
		atomic.AddInt32(&cb.halfOpenPermits, -1)
		// If enough successes in half-open, close the circuit
		summary := cb.metrics.Summary()
		if summary.Successes >= cb.config.MinimumRequests/2 && summary.ErrorRate < cb.config.ErrorThreshold {
			cb.transitionTo(StateClosed)
		}
	}
}

// RecordFailure records a failed operation and evaluates state.
func (cb *OmniCircuitBreaker) RecordFailure() {
	cb.metrics.RecordFailure()
	consecutive := atomic.AddInt64(&cb.consecutiveErrors, 1)

	state := cb.State()

	if state == StateHalfOpen {
		atomic.AddInt32(&cb.halfOpenPermits, -1)
		cb.transitionTo(StateOpen) // immediate trip on half-open failure
		return
	}

	if state == StateClosed {
		// Check consecutive failures
		if consecutive >= cb.config.MaxConsecutiveFailures {
			cb.transitionTo(StateOpen)
			return
		}

		// Check error rate threshold
		summary := cb.metrics.Summary()
		if summary.TotalOps >= cb.config.MinimumRequests && summary.ErrorRate >= cb.config.ErrorThreshold {
			cb.transitionTo(StateOpen)
		}
	}
}

// RecordTimeout records a timeout and treats it as a failure.
func (cb *OmniCircuitBreaker) RecordTimeout() {
	cb.metrics.RecordTimeout()
	cb.RecordFailure()
}

// transitionTo changes the circuit state.
func (cb *OmniCircuitBreaker) transitionTo(newState CircuitState) {
	cb.mu.Lock()
	oldState := CircuitState(atomic.LoadInt32(&cb.state))
	if oldState == newState {
		cb.mu.Unlock()
		return
	}

	atomic.StoreInt32(&cb.state, int32(newState))
	cb.lastStateChange = time.Now()
	cb.mu.Unlock()

	// Track statistics
	if newState == StateOpen {
		atomic.AddInt64(&cb.totalTrips, 1)
	} else if newState == StateClosed {
		atomic.AddInt64(&cb.totalResets, 1)
		cb.metrics.Reset()
		atomic.StoreInt64(&cb.consecutiveErrors, 0)
	}

	if newState == StateHalfOpen {
		atomic.StoreInt32(&cb.halfOpenPermits, 0)
	}

	// Notify callback
	if cb.config.OnStateChange != nil {
		go cb.config.OnStateChange(cb.config.Name, oldState, newState)
	}
}

// Reset manually resets the circuit to closed state.
func (cb *OmniCircuitBreaker) Reset() {
	cb.transitionTo(StateClosed)
}

// ForceOpen manually forces the circuit to open state.
func (cb *OmniCircuitBreaker) ForceOpen() {
	cb.transitionTo(StateOpen)
}

// Metrics returns the current sliding window metrics summary.
func (cb *OmniCircuitBreaker) Metrics() MetricsSummary {
	return cb.metrics.Summary()
}

// ── Deterministic Health Score ──────────────────────────────────────────────────

// HealthScore computes a deterministic health score [0.0, 1.0] based on metrics.
func (cb *OmniCircuitBreaker) HealthScore() float64 {
	summary := cb.metrics.Summary()
	if summary.TotalOps == 0 {
		return 1.0 // no data = healthy
	}

	// Health = 1 - error_rate, weighted by state
	baseHealth := 1.0 - summary.ErrorRate

	state := cb.State()
	switch state {
	case StateClosed:
		return baseHealth
	case StateHalfOpen:
		return baseHealth * 0.5
	case StateOpen:
		return 0.0
	}
	return baseHealth
}

// ── Fingerprint ─────────────────────────────────────────────────────────────────

// Fingerprint returns a deterministic SHA-256 hash of the circuit breaker configuration.
func (cb *OmniCircuitBreaker) Fingerprint() string {
	data := fmt.Sprintf("%s:%f:%d:%s:%d:%s:%d:%d",
		cb.config.Name,
		cb.config.ErrorThreshold,
		cb.config.MinimumRequests,
		cb.config.OpenDuration,
		cb.config.HalfOpenMaxRequests,
		cb.config.WindowSize,
		cb.config.WindowBuckets,
		cb.config.MaxConsecutiveFailures,
	)
	hash := sha256.Sum256([]byte(data))
	return hex.EncodeToString(hash[:])
}

// ── Diagnostics ─────────────────────────────────────────────────────────────────

// Diagnostics returns engine health status for the OMNI Engine Registry.
type DiagnosticsReport struct {
	EngineID          string         `json:"engine_id"`
	Version           string         `json:"version"`
	Status            string         `json:"status"`
	CircuitName       string         `json:"circuit_name"`
	State             string         `json:"state"`
	HealthScore       float64        `json:"health_score"`
	ErrorThreshold    float64        `json:"error_threshold"`
	OpenDuration      string         `json:"open_duration"`
	Metrics           MetricsSummary `json:"metrics"`
	TotalTrips        int64          `json:"total_trips"`
	TotalResets       int64          `json:"total_resets"`
	ConsecutiveErrors int64          `json:"consecutive_errors"`
	Fingerprint       string         `json:"fingerprint"`
	UptimeSeconds     float64        `json:"uptime_seconds"`
}

func (cb *OmniCircuitBreaker) Diagnostics() DiagnosticsReport {
	return DiagnosticsReport{
		EngineID:          EngineID,
		Version:           Version,
		Status:            "operational",
		CircuitName:       cb.config.Name,
		State:             cb.State().String(),
		HealthScore:       math.Round(cb.HealthScore()*10000) / 10000,
		ErrorThreshold:    cb.config.ErrorThreshold,
		OpenDuration:      cb.config.OpenDuration.String(),
		Metrics:           cb.Metrics(),
		TotalTrips:        atomic.LoadInt64(&cb.totalTrips),
		TotalResets:       atomic.LoadInt64(&cb.totalResets),
		ConsecutiveErrors: atomic.LoadInt64(&cb.consecutiveErrors),
		Fingerprint:       cb.Fingerprint()[:16],
		UptimeSeconds:     math.Round(time.Since(cb.createdAt).Seconds()*100) / 100,
	}
}

