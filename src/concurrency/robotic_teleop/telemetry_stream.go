package concurrency

import (
	"sync"
	"time"
)

type OmniResult struct {
	Value interface{}
	Error error
}

type TelemetryData struct {
	Timestamp int64
	Joints    []float64
	Voltage   float64
	TempC     float64
}

type TelemetryStream struct {
	subscribers []chan TelemetryData
	mu          sync.RWMutex
	running     bool
}

func NewTelemetryStream() *TelemetryStream {
	return &TelemetryStream{
		subscribers: make([]chan TelemetryData, 0),
		running:     false,
	}
}

func (t *TelemetryStream) Subscribe() chan TelemetryData {
	ch := make(chan TelemetryData, 100)
	t.mu.Lock()
	t.subscribers = append(t.subscribers, ch)
	t.mu.Unlock()
	return ch
}

func (t *TelemetryStream) StartSimulatedHardwareStream() {
	t.mu.Lock()
	if t.running {
		t.mu.Unlock()
		return
	}
	t.running = true
	t.mu.Unlock()

	go func() {
		// Deterministic hardware telemetry generation
		step := 0.0
		for {
			t.mu.RLock()
			if !t.running {
				t.mu.RUnlock()
				break
			}

			data := TelemetryData{
				Timestamp: time.Now().UnixNano(),
				Joints: []float64{
					step * 0.1,
					0.5,
					-0.5,
					step * 0.05,
					0.0,
					0.0,
				},
				Voltage: 24.0 - (float64(int(step)%10) * 0.1),
				TempC:   45.0 + (float64(int(step)%20) * 0.5),
			}

			for _, ch := range t.subscribers {
				select {
				case ch <- data:
				default:
				}
			}
			t.mu.RUnlock()

			step += 1.0
			time.Sleep(50 * time.Millisecond) // 20Hz update rate
		}
	}()
}

func (t *TelemetryStream) Stop() {
	t.mu.Lock()
	t.running = false
	t.mu.Unlock()
}
