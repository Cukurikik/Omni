package peft

import (
	"context"
	"fmt"
	"time"
)

// OMNI PEFT: Adapter Load Stream
// Go gRPC logic to emit events whenever a LoRA adapter is hot-swapped into a base model.
// Source: huggingface/peft

type AdapterLoadEvent struct {
	BaseModel   string
	AdapterName string
	Action      string // "LOAD", "UNLOAD", "MERGE"
	LatencyMs   float64
	Timestamp   int64
}

type AdapterEventStream struct {
	sinkChan chan AdapterLoadEvent
}

func NewAdapterEventStream(bufferSize int) *AdapterEventStream {
	return &AdapterEventStream{
		sinkChan: make(chan AdapterLoadEvent, bufferSize),
	}
}

// Emits an event non-blockingly
func (aes *AdapterEventStream) EmitLoad(base string, adapter string, action string, latency float64) {
	event := AdapterLoadEvent{
		BaseModel:   base,
		AdapterName: adapter,
		Action:      action,
		LatencyMs:   latency,
		Timestamp:   time.Now().UnixMilli(),
	}

	select {
	case aes.sinkChan <- event:
		// Sent
	default:
		fmt.Println("[Warning] PEFT Adapter stream buffer full, dropping telemetry.")
	}
}

// Background worker
func (aes *AdapterEventStream) Start(ctx context.Context) {
	go func() {
		for {
			select {
			case <-ctx.Done():
				return
			case event := <-aes.sinkChan:
				// Simulated push to Datadog/Prometheus
				fmt.Printf("[PEFT Telemetry] %s %s on %s | Latency: %.1fms\n",
					event.Action, event.AdapterName, event.BaseModel, event.LatencyMs)
			}
		}
	}()
}
