package concurrency

// Aria Research Assistant event bus
// Highly concurrent message broker for autonomous agents

import (
	"errors"
	"sync"
)

const MAX_TOPICS = 1000

type OmniBusResult struct {
	IsOk  bool
	Error error
}

type AriaBus struct {
	topics map[string]chan []byte
	mu     sync.RWMutex
}

func NewAriaBus() *AriaBus {
	return &AriaBus{
		topics: make(map[string]chan []byte),
	}
}

func (b *AriaBus) CreateTopic(name string) OmniBusResult {
	b.mu.Lock()
	defer b.mu.Unlock()

	if len(b.topics) >= MAX_TOPICS {
		return OmniBusResult{IsOk: false, Error: errors.New("Max topics exceeded")}
	}

	if _, exists := b.topics[name]; !exists {
		b.topics[name] = make(chan []byte, 1024)
	}
	return OmniBusResult{IsOk: true}
}

func (b *AriaBus) Publish(topic string, payload []byte) OmniBusResult {
	b.mu.RLock()
	ch, exists := b.topics[topic]
	b.mu.RUnlock()

	if !exists {
		return OmniBusResult{IsOk: false, Error: errors.New("Topic not found")}
	}

	select {
	case ch <- payload:
		return OmniBusResult{IsOk: true}
	default:
		return OmniBusResult{IsOk: false, Error: errors.New("Topic channel full")}
	}
}
