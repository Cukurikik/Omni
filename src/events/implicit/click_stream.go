package implicit

import (
	"time"
	"fmt"
	"context"
)

// OMNI IMPLICIT: Click Stream
// Go event streamer that captures user interactions (clicks, views) in real-time 
// and buffers them for batch matrix updates.
// Source: benfred/implicit

type Interaction struct {
	UserID    string
	ItemID    string
	EventType string
	Timestamp int64
}

type ClickStream struct {
	streamChan chan Interaction
}

func NewClickStream(bufferSize int) *ClickStream {
	return &ClickStream{
		streamChan: make(chan Interaction, bufferSize),
	}
}

func (c *ClickStream) Emit(user string, item string, eventType string) {
	evt := Interaction{
		UserID:    user,
		ItemID:    item,
		EventType: eventType,
		Timestamp: time.Now().UnixMilli(),
	}

	select {
	case c.streamChan <- evt:
	default:
		// Fallback for extreme traffic spikes
		fmt.Printf("[Implicit Stream] Buffer full, dropping %s event for user %s\n", eventType, user)
	}
}

// Background processor simulating write-behind cache or Kafka push
func (c *ClickStream) StartWorker(ctx context.Context) {
	go func() {
		fmt.Println("[Implicit Stream] Click worker started.")
		for {
			select {
			case <-ctx.Done():
				return
			case evt := <-c.streamChan:
				// Simulate writing to PostgreSQL or TimescaleDB
				fmt.Printf("[Data Ingestion] User: %s | Item: %s | Event: %s\n", 
					evt.UserID, evt.ItemID, evt.EventType)
			}
		}
	}()
}
