// omni_health_gateway.go — Health Check & Readiness Gateway
// Inspired by: Kubernetes readiness/liveness probes for model serving
// Layer: Network / Go
//
// HTTP gateway for model health monitoring with warm-up detection,
// memory pressure alerts, and cascading dependency checks.

package health

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
)

type ComponentStatus string

const (
	StatusHealthy   ComponentStatus = "healthy"
	StatusDegraded  ComponentStatus = "degraded"
	StatusUnhealthy ComponentStatus = "unhealthy"
	StatusUnknown   ComponentStatus = "unknown"
)

type ComponentHealth struct {
	Name      string          `json:"name"`
	Status    ComponentStatus `json:"status"`
	Message   string          `json:"message,omitempty"`
	LatencyMs float64         `json:"latency_ms"`
	LastCheck time.Time       `json:"last_check"`
	Metadata  map[string]any  `json:"metadata,omitempty"`
}

type OverallHealth struct {
	Status     ComponentStatus   `json:"status"`
	Timestamp  time.Time         `json:"timestamp"`
	Uptime     string            `json:"uptime"`
	Version    string            `json:"version"`
	Components []ComponentHealth `json:"components"`
	System     SystemInfo        `json:"system"`
}

type SystemInfo struct {
	GoRoutines  int     `json:"goroutines"`
	HeapAllocMB float64 `json:"heap_alloc_mb"`
	HeapSysMB   float64 `json:"heap_sys_mb"`
	NumGC       uint32  `json:"num_gc"`
	CPUCores    int     `json:"cpu_cores"`
}

type HealthChecker interface {
	Name() string
	Check(ctx context.Context) ComponentHealth
}

type ModelHealthChecker struct {
	modelName     string
	checkFunc     func(ctx context.Context) error
	warmupDone    atomic.Bool
	lastLatencyNs atomic.Int64
}

func NewModelHealthChecker(name string, checkFunc func(ctx context.Context) error) *ModelHealthChecker {
	return &ModelHealthChecker{
		modelName: name,
		checkFunc: checkFunc,
	}
}

func (m *ModelHealthChecker) Name() string { return m.modelName }

func (m *ModelHealthChecker) MarkWarmupDone() {
	m.warmupDone.Store(true)
}

func (m *ModelHealthChecker) Check(ctx context.Context) ComponentHealth {
	start := time.Now()
	health := ComponentHealth{
		Name:      m.modelName,
		LastCheck: start,
		Metadata:  make(map[string]any),
	}

	if !m.warmupDone.Load() {
		health.Status = StatusDegraded
		health.Message = "model warming up"
		health.LatencyMs = float64(time.Since(start).Milliseconds())
		return health
	}

	err := m.checkFunc(ctx)
	elapsed := time.Since(start)
	health.LatencyMs = float64(elapsed.Nanoseconds()) / 1e6
	m.lastLatencyNs.Store(int64(elapsed))

	if err != nil {
		health.Status = StatusUnhealthy
		health.Message = err.Error()
	} else if elapsed > 5*time.Second {
		health.Status = StatusDegraded
		health.Message = fmt.Sprintf("slow response: %.1fms", health.LatencyMs)
	} else {
		health.Status = StatusHealthy
		health.Message = "operational"
	}

	health.Metadata["warmup_complete"] = true
	health.Metadata["last_latency_ns"] = m.lastLatencyNs.Load()

	return health
}

type MemoryHealthChecker struct {
	thresholdMB float64
}

func NewMemoryHealthChecker(thresholdMB float64) *MemoryHealthChecker {
	return &MemoryHealthChecker{thresholdMB: thresholdMB}
}

func (m *MemoryHealthChecker) Name() string { return "memory" }

func (m *MemoryHealthChecker) Check(_ context.Context) ComponentHealth {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	heapMB := float64(memStats.HeapAlloc) / 1024 / 1024
	health := ComponentHealth{
		Name:      "memory",
		LastCheck: time.Now(),
		Metadata: map[string]any{
			"heap_alloc_mb": heapMB,
			"heap_sys_mb":   float64(memStats.HeapSys) / 1024 / 1024,
			"num_gc":        memStats.NumGC,
			"threshold_mb":  m.thresholdMB,
		},
	}

	if heapMB > m.thresholdMB {
		health.Status = StatusDegraded
		health.Message = fmt.Sprintf("heap %.1fMB exceeds threshold %.1fMB", heapMB, m.thresholdMB)
	} else {
		health.Status = StatusHealthy
		health.Message = fmt.Sprintf("heap %.1fMB", heapMB)
	}
	health.LatencyMs = 0

	return health
}

type OmniHealthGateway struct {
	mu        sync.RWMutex
	checkers  []HealthChecker
	startTime time.Time
	version   string
}

func NewHealthGateway(version string) *OmniHealthGateway {
	return &OmniHealthGateway{
		checkers:  make([]HealthChecker, 0),
		startTime: time.Now(),
		version:   version,
	}
}

func (g *OmniHealthGateway) Register(checker HealthChecker) {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.checkers = append(g.checkers, checker)
}

func (g *OmniHealthGateway) CheckAll(ctx context.Context) OverallHealth {
	g.mu.RLock()
	defer g.mu.RUnlock()

	components := make([]ComponentHealth, 0, len(g.checkers))
	overallStatus := StatusHealthy

	for _, checker := range g.checkers {
		health := checker.Check(ctx)
		components = append(components, health)

		switch health.Status {
		case StatusUnhealthy:
			overallStatus = StatusUnhealthy
		case StatusDegraded:
			if overallStatus != StatusUnhealthy {
				overallStatus = StatusDegraded
			}
		}
	}

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	return OverallHealth{
		Status:     overallStatus,
		Timestamp:  time.Now(),
		Uptime:     time.Since(g.startTime).Round(time.Second).String(),
		Version:    g.version,
		Components: components,
		System: SystemInfo{
			GoRoutines:  runtime.NumGoroutine(),
			HeapAllocMB: float64(memStats.HeapAlloc) / 1024 / 1024,
			HeapSysMB:   float64(memStats.HeapSys) / 1024 / 1024,
			NumGC:       memStats.NumGC,
			CPUCores:    runtime.NumCPU(),
		},
	}
}

func (g *OmniHealthGateway) HandleLiveness(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "alive"})
}

func (g *OmniHealthGateway) HandleReadiness(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
	defer cancel()

	health := g.CheckAll(ctx)
	w.Header().Set("Content-Type", "application/json")

	switch health.Status {
	case StatusHealthy:
		w.WriteHeader(http.StatusOK)
	case StatusDegraded:
		w.WriteHeader(http.StatusOK)
	default:
		w.WriteHeader(http.StatusServiceUnavailable)
	}

	json.NewEncoder(w).Encode(health)
}

func (g *OmniHealthGateway) HandleHealth(w http.ResponseWriter, r *http.Request) {
	ctx, cancel := context.WithTimeout(r.Context(), 15*time.Second)
	defer cancel()

	health := g.CheckAll(ctx)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(health)
}
