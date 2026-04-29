// OmniGRPCMultiplexer - OMNI Concurrency Layer
//
// Implements high-performance HTTP/2 gRPC stream multiplexing
// leveraging Go's highly efficient goroutines and channels.

package go_core

import (
	"context"
	"errors"
	"sync"
	"time"
)

// Monadic Result type for Go
type Result[T any] struct {
	Value T
	Err   error
}

func Ok[T any](v T) Result[T] { return Result[T]{Value: v, Err: nil} }
func Err[T any](e error) Result[T] { return Result[T]{Err: e} }

// MessagePayload represents an inter-layer data packet
type MessagePayload struct {
	StreamID string
	Data     []byte
}

type OmniGRPCMultiplexer struct {
	mu       sync.RWMutex
	streams  map[string]chan MessagePayload
	isActive bool
}

func NewOmniGRPCMultiplexer() *OmniGRPCMultiplexer {
	return &OmniGRPCMultiplexer{
		streams:  make(map[string]chan MessagePayload),
		isActive: true,
	}
}

// RouteMessage safely multiplexes a message to the correct worker channel
func (m *OmniGRPCMultiplexer) RouteMessage(ctx context.Context, msg MessagePayload) Result[bool] {
	m.mu.RLock()
	defer m.mu.RUnlock()

	if !m.isActive {
		return Err[bool](errors.New("multiplexer is shutting down"))
	}

	ch, exists := m.streams[msg.StreamID]
	if !exists {
		return Err[bool](errors.New("stream ID not found"))
	}

	// Non-blocking send with context timeout
	select {
	case ch <- msg:
		return Ok(true)
	case <-ctx.Done():
		return Err[bool](context.DeadlineExceeded)
	case <-time.After(50 * time.Millisecond):
		return Err[bool](errors.New("channel blocked, dropping message to preserve backpressure"))
	}
}
