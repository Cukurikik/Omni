package network_gocore

import (
	"context"
	"sync"
	"time"
)

// RobustnessTelemetry logs OOD metrics from the NLP engine.
type RobustnessTelemetry struct {
	mu            sync.RWMutex
	OodEventCount uint64
	TotalRequests uint64
	Logs          []OODEvent
}

type OODEvent struct {
	Timestamp  time.Time
	ModelID    string
	Distance   float64
	Confidence float64
}

func NewRobustnessTelemetry() *RobustnessTelemetry {
	return &RobustnessTelemetry{
		Logs: make([]OODEvent, 0),
	}
}

func (r *RobustnessTelemetry) RecordRequest(ctx context.Context, isOod bool, modelID string, dist float64, conf float64) {
	r.mu.Lock()
	defer r.mu.Unlock()

	r.TotalRequests++
	if isOod {
		r.OodEventCount++
		r.Logs = append(r.Logs, OODEvent{
			Timestamp:  time.Now(),
			ModelID:    modelID,
			Distance:   dist,
			Confidence: conf,
		})

		// Keep log size bounded
		if len(r.Logs) > 1000 {
			r.Logs = r.Logs[100:]
		}
	}
}

func (r *RobustnessTelemetry) GetStats() (uint64, uint64) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return r.TotalRequests, r.OodEventCount
}

