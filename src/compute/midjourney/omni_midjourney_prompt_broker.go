// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Midjourney Broker Queue (OMNI Production-Grade Implementation)
// Implements Go channels concurrent message dispatch with context cancellation,
// prompt validation, metrics tracking, and error recovery.

package midjourney

import (
	"context"
	"errors"
	"fmt"
	"log"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// Result acts as our Monadic type in Go
type Result struct {
	Value   string
	Error   error
	Success bool
}

type OmniResult struct {
	Value interface{}
	Error error
}

func Ok(val interface{}) OmniResult {
	return OmniResult{Value: val, Error: nil}
}

func Fail(err string) OmniResult {
	return OmniResult{Value: nil, Error: errors.New(err)}
}

func OkResult(val string) Result {
	return Result{val, nil, true}
}

func FailResult(err string) Result {
	return Result{"", errors.New(err), false}
}

// Prompt validation constants
const (
	MaxPromptLength = 6000
	MinPromptLength = 3
	MaxQueueSize    = 1000
	DispatchTimeout = 30 * time.Second
	MaxRetries      = 3
	RetryBackoff    = 500 * time.Millisecond
)

var (
	ErrEmptyPrompt        = errors.New("prompt cannot be empty")
	ErrPromptTooShort     = fmt.Errorf("prompt too short (minimum %d characters)", MinPromptLength)
	ErrPromptTooLong      = fmt.Errorf("prompt exceeds maximum length (%d characters)", MaxPromptLength)
	ErrQueueOverflow      = errors.New("queue overflow: worker pool busy")
	ErrDispatchTimeout    = errors.New("dispatch timed out")
	ErrMaxRetriesExceeded = errors.New("max retries exceeded")
	ErrBrokerShuttingDown = errors.New("broker shutting down")
)

// PromptRequest represents a Midjourney image generation request
type PromptRequest struct {
	JobID      string
	Prompt     string
	Model      string // "midjourney-v6", "midjourney-niji", etc.
	AspectRat  string // "16:9", "1:1", "9:16", etc.
	CreatedAt  time.Time
	RetryCount int
}

// BrokerMetrics tracks operational metrics using atomic counters
type BrokerMetrics struct {
	TotalDispatched  atomic.Int64
	TotalFailed      atomic.Int64
	TotalRetries     atomic.Int64
	avgLatencyMs     float64
	latencyMu        sync.Mutex
	LastActivityTime atomic.Int64 // unix timestamp
}

func (m *BrokerMetrics) GetAvgLatency() float64 {
	m.latencyMu.Lock()
	defer m.latencyMu.Unlock()
	return m.avgLatencyMs
}

func (m *BrokerMetrics) SetAvgLatency(v float64) {
	m.latencyMu.Lock()
	defer m.latencyMu.Unlock()
	m.avgLatencyMs = v
}

// BrokerQueue manages concurrent prompt dispatch with backpressure
type BrokerQueue struct {
	Inbound     chan PromptRequest
	Outbound    chan string
	mu          sync.RWMutex
	metrics     BrokerMetrics
	bannedWords []string
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewBrokerQueue creates a new production-grade broker queue
func NewBrokerQueue(bufferSize int) *BrokerQueue {
	if bufferSize <= 0 || bufferSize > MaxQueueSize {
		bufferSize = MaxQueueSize
	}

	ctx, cancel := context.WithCancel(context.Background())

	bq := &BrokerQueue{
		Inbound:  make(chan PromptRequest, bufferSize),
		Outbound: make(chan string, bufferSize),
		metrics:  BrokerMetrics{},
		bannedWords: []string{
			"nsfw", "nude", "naked", "explicit", "gore",
			"violence", "hate", "discriminatory",
		},
		ctx:    ctx,
		cancel: cancel,
	}

	// Start background metrics reporter
	go bq.metricsReporter(ctx)

	return bq
}

// ValidatePrompt performs comprehensive prompt validation
func (bq *BrokerQueue) ValidatePrompt(prompt string) error {
	if prompt == "" {
		return ErrEmptyPrompt
	}

	if len(prompt) < MinPromptLength {
		return ErrPromptTooShort
	}

	if len(prompt) > MaxPromptLength {
		return ErrPromptTooLong
	}

	// Check for banned words
	lower := strings.ToLower(prompt)
	for _, word := range bq.bannedWords {
		if strings.Contains(lower, word) {
			return fmt.Errorf("prompt contains banned word: %q", word)
		}
	}

	// Check for SQL injection patterns
	sqlPatterns := []string{"DROP TABLE", "DELETE FROM", "INSERT INTO", "UNION SELECT", "'; --"}
	for _, pattern := range sqlPatterns {
		if strings.Contains(strings.ToUpper(prompt), pattern) {
			return fmt.Errorf("prompt contains suspicious SQL pattern")
		}
	}

	// Check for XSS patterns
	xssPatterns := []string{"<script", "javascript:", "onerror=", "onload="}
	for _, pattern := range xssPatterns {
		if strings.Contains(strings.ToLower(prompt), pattern) {
			return fmt.Errorf("prompt contains suspicious XSS pattern")
		}
	}

	return nil
}

// Dispatch sends a prompt through the broker queue with timeout and retry logic
func (bq *BrokerQueue) Dispatch(req PromptRequest) Result {
	// Validate first
	if err := bq.ValidatePrompt(req.Prompt); err != nil {
		log.Printf("[ERROR] Validation failed for job %s: %v", req.JobID, err)
		bq.metrics.TotalFailed.Add(1)
		return FailResult(err.Error())
	}

	// Set defaults
	if req.Model == "" {
		req.Model = "midjourney-v6"
	}
	if req.AspectRat == "" {
		req.AspectRat = "1:1"
	}
	req.CreatedAt = time.Now()

	// Dispatch with retry
	var lastErr error
	for attempt := 0; attempt < MaxRetries; attempt++ {
		if attempt > 0 {
			bq.metrics.TotalRetries.Add(1)
			log.Printf("[WARN] Retry %d/%d for job %s", attempt, MaxRetries, req.JobID)
			select {
			case <-time.After(RetryBackoff * time.Duration(attempt)):
			case <-bq.ctx.Done():
				return FailResult(ErrBrokerShuttingDown.Error())
			}
		}

		result := bq.tryDispatch(req)
		if result.Success {
			bq.metrics.TotalDispatched.Add(1)
			bq.metrics.LastActivityTime.Store(time.Now().Unix())
			log.Printf("[OK] Dispatched job %s (model=%s, ratio=%s)", req.JobID, req.Model, req.AspectRat)
			return result
		}

		lastErr = result.Error
	}

	bq.metrics.TotalFailed.Add(1)
	log.Printf("[ERROR] Job %s failed after %d retries: %v", req.JobID, MaxRetries, lastErr)
	return Result{"", fmt.Errorf("%w: %v", ErrMaxRetriesExceeded, lastErr), false}
}

// tryDispatch attempts a single dispatch operation with context timeout
func (bq *BrokerQueue) tryDispatch(req PromptRequest) Result {
	startTime := time.Now()

	ctx, cancel := context.WithTimeout(bq.ctx, DispatchTimeout)
	defer cancel()

	select {
	case <-ctx.Done():
		latency := time.Since(startTime).Milliseconds()
		bq.updateAvgLatency(latency)
		return FailResult(fmt.Sprintf("%v (after %dms)", ErrDispatchTimeout, latency))

	case bq.Inbound <- req:
		// Process and format outbound message with structured URI-like format
		processed := fmt.Sprintf("mj://%s|%s|%s|%s", req.Model, req.AspectRat, req.JobID, hashPrompt(req.Prompt))

		select {
		case bq.Outbound <- processed:
			latency := time.Since(startTime).Milliseconds()
			bq.updateAvgLatency(latency)
			return OkResult(processed)
		case <-ctx.Done():
			return FailResult(ErrQueueOverflow.Error())
		}

	default:
		latency := time.Since(startTime).Milliseconds()
		bq.updateAvgLatency(latency)
		return FailResult(ErrQueueOverflow.Error())
	}
}

// GetMetrics returns current broker metrics
func (bq *BrokerQueue) GetMetrics() map[string]interface{} {
	bq.mu.RLock()
	defer bq.mu.RUnlock()

	return map[string]interface{}{
		"total_dispatched": bq.metrics.TotalDispatched.Load(),
		"total_failed":     bq.metrics.TotalFailed.Load(),
		"total_retries":    bq.metrics.TotalRetries.Load(),
		"avg_latency_ms":   bq.metrics.GetAvgLatency(),
		"last_activity":    time.Unix(bq.metrics.LastActivityTime.Load(), 0).Format(time.RFC3339),
		"queue_size":       len(bq.Inbound),
		"outbound_queue":   len(bq.Outbound),
	}
}

// Shutdown gracefully shuts down the broker queue
func (bq *BrokerQueue) Shutdown() {
	log.Println("[INFO] Shutting down broker queue...")
	bq.cancel()

	// Drain channels
	close(bq.Inbound)
	close(bq.Outbound)

	log.Println("[INFO] Broker queue shut down gracefully")
}

// Internal helpers

func (bq *BrokerQueue) updateAvgLatency(newLatencyMs int64) {
	// Exponential moving average
	oldAvg := bq.metrics.GetAvgLatency()
	newAvg := oldAvg*0.9 + float64(newLatencyMs)*0.1
	bq.metrics.SetAvgLatency(newAvg)
}

func (bq *BrokerQueue) metricsReporter(ctx context.Context) {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			m := bq.GetMetrics()
			log.Printf("[METRICS] dispatched=%v, failed=%v, retries=%v, avg_latency=%.1fms",
				m["total_dispatched"], m["total_failed"], m["total_retries"], m["avg_latency_ms"])
		}
	}
}

// hashPrompt creates a short deterministic hash of the prompt for tracking
func hashPrompt(prompt string) string {
	h := uint64(0)
	for _, c := range prompt {
		h = h*31 + uint64(c)
	}
	return fmt.Sprintf("%08x", h)
}
