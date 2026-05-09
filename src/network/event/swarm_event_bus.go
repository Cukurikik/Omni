//=============================================================================
// OMNI NETWORK LAYER — SWARM AGENT EVENT BUS (GO)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: High-speed publish/subscribe message bus specifically for
//              inter-agent communication in the Swarms framework.
//=============================================================================

package event

import (
	"sync"
)

type SwarmMessage struct {
	SenderID   string
	ReceiverID string // Empty if broadcast
	Topic      string
	Payload    []byte
}

type SwarmEventBus struct {
	subscribers map[string][]chan SwarmMessage
	mu          sync.RWMutex
}

func NewSwarmEventBus() *SwarmEventBus {
	return &SwarmEventBus{
		subscribers: make(map[string][]chan SwarmMessage),
	}
}

// Subscribe an agent to a topic
func (b *SwarmEventBus) Subscribe(topic string) chan SwarmMessage {
	b.mu.Lock()
	defer b.mu.Unlock()

	ch := make(chan SwarmMessage, 100)
	b.subscribers[topic] = append(b.subscribers[topic], ch)
	return ch
}

// Publish sends a message to all agents subscribed to the topic
func (b *SwarmEventBus) Publish(msg SwarmMessage) {
	b.mu.RLock()
	defer b.mu.RUnlock()

	if chans, found := b.subscribers[msg.Topic]; found {
		for _, ch := range chans {
			// Non-blocking send
			select {
			case ch <- msg:
			default:
				// If channel is full, drop message (or handle via DLQ)
			}
		}
	}
}
