package autogpt

import (
	"context"
	"fmt"
	"time"
)

// OMNI AUTOGPT: Agent Event Emitter
// Go routines to emit autonomous agent thoughts, actions, and observations to a central telemetry hub.
// Source: Significant-Gravitas/AutoGPT

type EventType string

const (
	EventThought     EventType = "THOUGHT"
	EventAction      EventType = "ACTION"
	EventObservation EventType = "OBSERVATION"
	EventError       EventType = "ERROR"
)

type AgentEvent struct {
	AgentID   string
	Type      EventType
	Content   string
	Timestamp int64
}

type EventEmitterError struct {
	Message string
}

func (e *EventEmitterError) Error() string { return e.Message }

type AgentEventEmitter struct {
	sinkChan chan AgentEvent
}

func NewEventEmitter(bufferSize int) *AgentEventEmitter {
	return &AgentEventEmitter{
		sinkChan: make(chan AgentEvent, bufferSize),
	}
}

// Emits an event non-blockingly. If the buffer is full, drops the event to prevent agent lockup.
func (ae *AgentEventEmitter) Emit(agentID string, eventType EventType, content string) error {
	if agentID == "" {
		return &EventEmitterError{"AgentID cannot be empty"}
	}

	event := AgentEvent{
		AgentID:   agentID,
		Type:      eventType,
		Content:   content,
		Timestamp: time.Now().UnixMilli(),
	}

	select {
	case ae.sinkChan <- event:
		return nil
	default:
		return &EventEmitterError{"Event dropped: sink channel is full"}
	}
}

// Background worker to process and flush events to persistent storage/logs
func (ae *AgentEventEmitter) StartProcessor(ctx context.Context) {
	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("[AutoGPT Emitter] Shutting down processor.")
				return
			case event := <-ae.sinkChan:
				// In production, this pushes to Kafka or a DB
				fmt.Printf("[Agent %s] %s: %s\n", event.AgentID, event.Type, event.Content)
			}
		}
	}()
}
