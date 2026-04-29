package swanlab

import (
	"time"
	"fmt"
	"context"
	"log"
)

// OMNI SWANLAB: Log Stream
// Go channel-based streaming service that ingests real-time training logs 
// from running experiments and flushes them to database or WebSockets.
// Source: SwanHubX/SwanLab

type MetricLog struct {
	RunID     string
	Step      int
	Metrics   map[string]float64
	Timestamp int64
}

type LogIngester struct {
	logChan chan MetricLog
}

func NewLogIngester(bufferSize int) *LogIngester {
	return &LogIngester{
		logChan: make(chan MetricLog, bufferSize),
	}
}

// Thread-safe async metric ingestion
func (l *LogIngester) Emit(runID string, step int, metrics map[string]float64) {
	log := MetricLog{
		RunID:     runID,
		Step:      step,
		Metrics:   metrics,
		Timestamp: time.Now().UnixMilli(),
	}

	select {
	case l.logChan <- log:
		// Success
	default:
		fmt.Printf("[SwanLab] Warning: Log buffer full. Dropping metrics for run %s step %d\n", runID, step)
	}
}

// Background processor to batch insert into DB or push to UI
func (l *LogIngester) StartProcessing(ctx context.Context) {
	go func() {
		fmt.Println("[SwanLab] Log Ingester started.")
		for {
			select {
			case <-ctx.Done():
				fmt.Println("[SwanLab] Log Ingester shutting down.")
				return
			case log := <-l.logChan:
				// Simulate flushing to storage
				fmt.Printf("[DB Write] Run: %s | Step: %d | Metrics: %v\n", log.RunID, log.Step, log.Metrics)
			}
		}
	}()
}
