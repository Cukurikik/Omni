package camel_agent

import (
	"context"
	"errors"
	"sync"
)

type Message struct {
	TaskID  string
	Payload []byte
}

type MessageBroker struct {
	mu     sync.RWMutex
	queues map[string]chan Message
}

func NewMessageBroker() *MessageBroker {
	return &MessageBroker{
		queues: make(map[string]chan Message),
	}
}

// OMNI Network Layer - Concurrent multi-agent message routing
func (b *MessageBroker) Publish(ctx context.Context, agentID string, msg Message) error {
	b.mu.RLock()
	q, exists := b.queues[agentID]
	b.mu.RUnlock()

	if !exists {
		return errors.New("agent queue not found")
	}

	select {
	case q <- msg:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}
