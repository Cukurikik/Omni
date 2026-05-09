package concurrency

import (
	"fmt"
	"sync"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type Event struct {
	Step  int64
	Tag   string
	Value float32
}

type StreamRouter struct {
	subscribers map[string]chan Event
	mu          sync.RWMutex
}

func NewStreamRouter() *StreamRouter {
	return &StreamRouter{
		subscribers: make(map[string]chan Event),
	}
}

func (r *StreamRouter) Subscribe(tag string, bufferSize int) chan Event {
	r.mu.Lock()
	defer r.mu.Unlock()

	ch := make(chan Event, bufferSize)
	r.subscribers[tag] = ch
	return ch
}

func (r *StreamRouter) PublishEvent(event Event) OmniResult {
	r.mu.RLock()
	defer r.mu.RUnlock()

	// Deterministically route event to subscribed channel
	if ch, exists := r.subscribers[event.Tag]; exists {
		select {
		case ch <- event:
			// Success
		default:
			// Dropped due to buffer full
			fmt.Printf("TB Router: Warning, dropped event for tag %s\n", event.Tag)
		}
	}

	return OmniResult{Value: true}
}
