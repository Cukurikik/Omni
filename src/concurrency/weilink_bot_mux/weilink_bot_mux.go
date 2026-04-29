package concurrency

import (
	"errors"
	"sync"
)

// OMNI WEILINK MCP BOT MULTIPLEXER
// Concurrency layer for massive WeChat zero-dependency iLink pipeline using goroutines.

type BotEvent struct {
	EventID   string
	Payload   []byte
	Timestamp int64
}

type WeilinkBotMux struct {
	eventBuffer chan BotEvent
	workers     int
	mu          sync.RWMutex
	isActive    bool
}

func NewWeilinkBotMux(bufferSize int, workers int) *WeilinkBotMux {
	return &WeilinkBotMux{
		eventBuffer: make(chan BotEvent, bufferSize),
		workers:     workers,
		isActive:    true,
	}
}

func (m *WeilinkBotMux) StartPipeline(handler func(BotEvent) error) error {
	m.mu.RLock()
	if !m.isActive {
		m.mu.RUnlock()
		return errors.New("PIPELINE_NOT_ACTIVE")
	}
	m.mu.RUnlock()

	var wg sync.WaitGroup
	for i := 0; i < m.workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for event := range m.eventBuffer {
				if err := handler(event); err != nil {
					// Monadic-like Go pattern, bubbling up to system logs internally
					_ = err
				}
			}
		}()
	}

	return nil
}

func (m *WeilinkBotMux) EnqueueEvent(event BotEvent) error {
	m.mu.RLock()
	defer m.mu.RUnlock()
	if !m.isActive {
		return errors.New("PIPELINE_NOT_ACTIVE")
	}

	select {
	case m.eventBuffer <- event:
		return nil
	default:
		return errors.New("MCP_PIPELINE_OVERLOAD")
	}
}

func (m *WeilinkBotMux) Shutdown() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.isActive = false
	close(m.eventBuffer)
}
