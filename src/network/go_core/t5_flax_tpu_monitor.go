package network_gocore

import (
	"context"
	"sync"
	"time"
)

// TpuMonitor tracks the health and utilization of GCP TPU Pods.
type TpuMonitor struct {
	mu           sync.RWMutex
	PodID        string
	Status       string
	MemoryUsage  float64
	ComputeUsage float64
	LastPing     time.Time
}

func NewTpuMonitor(podID string) *TpuMonitor {
	return &TpuMonitor{
		PodID:  podID,
		Status: "INITIALIZING",
	}
}

func (m *TpuMonitor) UpdateTelemetry(ctx context.Context, mem float64, comp float64) {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.MemoryUsage = mem
	m.ComputeUsage = comp
	m.Status = "TRAINING"
	m.LastPing = time.Now()
}

func (m *TpuMonitor) IsHealthy() bool {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return time.Since(m.LastPing) < 30*time.Second && m.Status == "TRAINING"
}

