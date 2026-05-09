package concurrency

import (
	"fmt"
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type AgentEvent struct {
	EventID   string
	Timestamp int64
	Payload   []float64
}

type AgenticEventLoop struct {
	events chan AgentEvent
	wg     sync.WaitGroup
	mu     sync.Mutex
	active bool
}

func NewAgenticEventLoop(bufferSize int) *AgenticEventLoop {
	return &AgenticEventLoop{
		events: make(chan AgentEvent, bufferSize),
		active: false,
	}
}

func (l *AgenticEventLoop) Start() {
	l.mu.Lock()
	if l.active {
		l.mu.Unlock()
		return
	}
	l.active = true
	l.mu.Unlock()

	l.wg.Add(1)
	go func() {
		defer l.wg.Done()
		for event := range l.events {
			// Deterministic event processing simulation
			_ = fmt.Sprintf("Processing event %s at %d", event.EventID, event.Timestamp)
		}
	}()
}

func (l *AgenticEventLoop) Dispatch(payload []float64) OmniResult {
	l.mu.Lock()
	defer l.mu.Unlock()

	if !l.active {
		return OmniResult{Error: fmt.Errorf("event loop is not active")}
	}

	event := AgentEvent{
		EventID:   fmt.Sprintf("EVT-%d", time.Now().UnixNano()),
		Timestamp: time.Now().UnixMilli(),
		Payload:   payload,
	}

	select {
	case l.events <- event:
		return OmniResult{Value: event.EventID}
	default:
		return OmniResult{Error: fmt.Errorf("event loop buffer full")}
	}
}

func (l *AgenticEventLoop) Stop() {
	l.mu.Lock()
	defer l.mu.Unlock()

	if l.active {
		l.active = false
		close(l.events)
		l.wg.Wait()
	}
}
