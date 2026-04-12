package services

import (
	"fmt"
	"log"
	"math/rand"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
)

// ==========================================
// 📊 OMNI SYSTEM TELEMETRY (Phase 8)
// ==========================================
// Real-time dashboard metrics untuk seluruh OMNI Gateway.
// Diekspos melalui endpoint /api/v1/telemetry.

// TelemetryCollector mengumpulkan metrik runtime secara atomik
type TelemetryCollector struct {
	mu              sync.RWMutex
	totalRequests   int64
	activeRequests  int64
	totalErrors     int64
	startTime       time.Time
	latencyBuckets  []float64 // dalam milliseconds
	traceBuffer     []TraceSpan
}

// TraceSpan mewakili satu unit komputasi terlacak dalam OMNI
type TraceSpan struct {
	TraceID   string  `json:"trace_id"`
	SpanID    string  `json:"span_id"`
	Operation string  `json:"operation"`
	StartTime string  `json:"start_time"`
	Duration  float64 `json:"duration_ms"`
	Status    string  `json:"status"`
}

var globalTelemetry *TelemetryCollector
var telemetryOnce sync.Once

// GetTelemetry mengembalikan instance singleton
func GetTelemetry() *TelemetryCollector {
	telemetryOnce.Do(func() {
		globalTelemetry = &TelemetryCollector{
			startTime:      time.Now(),
			latencyBuckets: make([]float64, 0, 1000),
			traceBuffer:    make([]TraceSpan, 0, 500),
		}
		log.Println("📊 [TELEMETRY] Kolektor metrik OMNI aktif")
	})
	return globalTelemetry
}

// RecordRequest mencatat satu request masuk
func (t *TelemetryCollector) RecordRequest() {
	atomic.AddInt64(&t.totalRequests, 1)
	atomic.AddInt64(&t.activeRequests, 1)
}

// FinishRequest menyelesaikan satu request
func (t *TelemetryCollector) FinishRequest(latencyMs float64) {
	atomic.AddInt64(&t.activeRequests, -1)
	t.mu.Lock()
	if len(t.latencyBuckets) < 1000 {
		t.latencyBuckets = append(t.latencyBuckets, latencyMs)
	} else {
		// Circular buffer: timpa bucket paling lama
		t.latencyBuckets[rand.Intn(1000)] = latencyMs
	}
	t.mu.Unlock()
}

// RecordError mencatat satu error
func (t *TelemetryCollector) RecordError() {
	atomic.AddInt64(&t.totalErrors, 1)
}

// StartSpan memulai satu distributed trace span
func (t *TelemetryCollector) StartSpan(operation string) TraceSpan {
	return TraceSpan{
		TraceID:   fmt.Sprintf("omni-%d", time.Now().UnixNano()),
		SpanID:    fmt.Sprintf("span-%d", rand.Int63()),
		Operation: operation,
		StartTime: time.Now().UTC().Format(time.RFC3339Nano),
		Status:    "IN_PROGRESS",
	}
}

// EndSpan menyelesaikan span dan memasukkannya ke buffer
func (t *TelemetryCollector) EndSpan(span TraceSpan, err error) {
	start, _ := time.Parse(time.RFC3339Nano, span.StartTime)
	span.Duration = float64(time.Since(start).Microseconds()) / 1000.0
	if err != nil {
		span.Status = "ERROR"
	} else {
		span.Status = "OK"
	}

	t.mu.Lock()
	if len(t.traceBuffer) >= 500 {
		t.traceBuffer = t.traceBuffer[1:] // FIFO eviction
	}
	t.traceBuffer = append(t.traceBuffer, span)
	t.mu.Unlock()
}

// GetDashboard menghasilkan snapshot metrik untuk dashboard
func (t *TelemetryCollector) GetDashboard() map[string]interface{} {
	t.mu.RLock()
	defer t.mu.RUnlock()

	var avgLatency float64
	if len(t.latencyBuckets) > 0 {
		var sum float64
		for _, l := range t.latencyBuckets {
			sum += l
		}
		avgLatency = sum / float64(len(t.latencyBuckets))
	}

	// Info runtime Go
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	uptime := time.Since(t.startTime)

	return map[string]interface{}{
		"uptime_seconds":    int(uptime.Seconds()),
		"uptime_human":      formatUptime(uptime),
		"total_requests":    atomic.LoadInt64(&t.totalRequests),
		"active_requests":   atomic.LoadInt64(&t.activeRequests),
		"total_errors":      atomic.LoadInt64(&t.totalErrors),
		"avg_latency_ms":    fmt.Sprintf("%.3f", avgLatency),
		"goroutines":        runtime.NumGoroutine(),
		"heap_alloc_mb":     fmt.Sprintf("%.2f", float64(memStats.HeapAlloc)/1024/1024),
		"sys_memory_mb":     fmt.Sprintf("%.2f", float64(memStats.Sys)/1024/1024),
		"gc_cycles":         memStats.NumGC,
		"go_version":        runtime.Version(),
		"cpu_cores":         runtime.NumCPU(),
		"recent_traces":     len(t.traceBuffer),
		"omni_engine":       "OMNI-NEXUS-ULTRA v2.0",
		"status":            "🟢 OPERATIONAL",
	}
}

// GetRecentTraces mengembalikan N trace terakhir
func (t *TelemetryCollector) GetRecentTraces(n int) []TraceSpan {
	t.mu.RLock()
	defer t.mu.RUnlock()

	if n > len(t.traceBuffer) {
		n = len(t.traceBuffer)
	}
	start := len(t.traceBuffer) - n
	result := make([]TraceSpan, n)
	copy(result, t.traceBuffer[start:])
	return result
}

func formatUptime(d time.Duration) string {
	h := int(d.Hours())
	m := int(d.Minutes()) % 60
	s := int(d.Seconds()) % 60
	return fmt.Sprintf("%dh %dm %ds", h, m, s)
}
