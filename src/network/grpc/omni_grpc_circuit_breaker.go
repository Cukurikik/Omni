package grpc

// omni_grpc_circuit_breaker.go — gRPC Circuit Breaker
// Layer: Network / Go
//
// Implements the Circuit Breaker pattern to prevent cascading failures
// in OMNI microservice mesh communication. Zero mock.

import (
	"context"
	"errors"
	"sync"
	"time"

	"google.golang.org/grpc"
)

type CircuitState int

const (
	StateClosed   CircuitState = iota // Normal operation
	StateOpen                         // Failing, reject requests
	StateHalfOpen                     // Testing recovery
)

var ErrCircuitOpen = errors.New("circuit breaker is OPEN")

type OmniCircuitBreaker struct {
	mu sync.RWMutex

	failureThreshold uint32
	failureCount     uint32
	successThreshold uint32
	successCount     uint32
	timeout          time.Duration

	state       CircuitState
	lastFailure time.Time
}

func NewOmniCircuitBreaker(failThresh uint32, successThresh uint32, timeout time.Duration) *OmniCircuitBreaker {
	return &OmniCircuitBreaker{
		failureThreshold: failThresh,
		successThreshold: successThresh,
		timeout:          timeout,
		state:            StateClosed,
	}
}

func (cb *OmniCircuitBreaker) AllowRequest() bool {
	cb.mu.RLock()
	currentState := cb.state
	lastFail := cb.lastFailure
	timeout := cb.timeout
	cb.mu.RUnlock()

	if currentState == StateClosed {
		return true
	}

	if currentState == StateOpen {
		if time.Since(lastFail) > timeout {
			cb.mu.Lock()
			// Double check
			if cb.state == StateOpen {
				cb.state = StateHalfOpen
				cb.successCount = 0
			}
			cb.mu.Unlock()
			return true
		}
		return false
	}

	// StateHalfOpen allows requests through to test
	return true
}

func (cb *OmniCircuitBreaker) RecordSuccess() {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	if cb.state == StateHalfOpen {
		cb.successCount++
		if cb.successCount >= cb.successThreshold {
			cb.state = StateClosed
			cb.failureCount = 0
		}
	} else if cb.state == StateClosed {
		cb.failureCount = 0
	}
}

func (cb *OmniCircuitBreaker) RecordFailure() {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	cb.failureCount++
	cb.lastFailure = time.Now()

	if cb.state == StateClosed && cb.failureCount >= cb.failureThreshold {
		cb.state = StateOpen
	} else if cb.state == StateHalfOpen {
		cb.state = StateOpen // Immediate failure if testing
	}
}

// UnaryClientInterceptor injects the circuit breaker into gRPC calls.
func (cb *OmniCircuitBreaker) UnaryClientInterceptor() grpc.UnaryClientInterceptor {
	return func(
		ctx context.Context,
		method string,
		req, reply interface{},
		cc *grpc.ClientConn,
		invoker grpc.UnaryInvoker,
		opts ...grpc.CallOption,
	) error {
		if !cb.AllowRequest() {
			return ErrCircuitOpen
		}

		err := invoker(ctx, method, req, reply, cc, opts...)

		if err != nil {
			cb.RecordFailure()
		} else {
			cb.RecordSuccess()
		}

		return err
	}
}

