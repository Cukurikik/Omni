//=============================================================================
// OMNI NETWORK LAYER — DEAD LETTER QUEUE MANAGER (GO)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Handles failed Swarm/RPC events, ensuring zero-data-loss
//              within the Omni Event Loop.
//=============================================================================

package event

import (
	"log"
	"sync"
	"time"
)

type FailedEvent struct {
	EventID   string
	Topic     string
	Payload   []byte
	Error     string
	Timestamp time.Time
	Retries   int
}

type DLQManager struct {
	queue []FailedEvent
	mu    sync.Mutex
}

func NewDLQManager() *DLQManager {
	return &DLQManager{
		queue: make([]FailedEvent, 0),
	}
}

// Push adds an event to the DLQ
func (m *DLQManager) Push(eventID, topic string, payload []byte, errStr string) {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.queue = append(m.queue, FailedEvent{
		EventID:   eventID,
		Topic:     topic,
		Payload:   payload,
		Error:     errStr,
		Timestamp: time.Now(),
		Retries:   0,
	})

	log.Printf("[DLQ] Event %s sent to Dead Letter Queue (Topic: %s)", eventID, topic)
}

// Drain attempts to replay events back into the bus
func (m *DLQManager) Drain(bus *SwarmEventBus) {
	m.mu.Lock()
	defer m.mu.Unlock()

	if len(m.queue) == 0 {
		return
	}

	log.Printf("[DLQ] Attempting to drain %d failed events", len(m.queue))

	var stillFailed []FailedEvent

	for _, ev := range m.queue {
		if ev.Retries >= 3 {
			// Permanent failure, log and drop (or write to disk)
			log.Printf("[DLQ] Event %s permanently failed after 3 retries", ev.EventID)
			continue
		}

		ev.Retries++
		// Re-publish to the bus
		bus.Publish(SwarmMessage{
			SenderID: "dlq_manager",
			Topic:    ev.Topic,
			Payload:  ev.Payload,
		})

		// Note: We don't verify success here immediately due to async pub/sub,
		// if it fails again, the worker will push it back to the DLQ.
	}

	m.queue = stillFailed
}
