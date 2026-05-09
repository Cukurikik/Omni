// moe_telemetry.go — MoE Inference Telemetry and Observability
// Layer: Network / Monitoring — MoE Observability
//
// Real-time telemetry collection for MoE inference: expert utilization
// heatmaps, routing entropy tracking, latency percentiles, and
// expert drift detection.

package network_moe

import (
	"math"
	"sort"
	"sync"
	"time"
)

// ExpertTelemetry captures per-expert performance metrics.
type ExpertTelemetry struct {
	ExpertID     int
	TokensRouted int64
	TotalWeight  float64
	Latencies    []float64
	ErrorCount   int64
	LastActive   time.Time
}

func (et *ExpertTelemetry) AvgWeight() float64 {
	if et.TokensRouted == 0 {
		return 0
	}
	return et.TotalWeight / float64(et.TokensRouted)
}

func (et *ExpertTelemetry) P50Latency() float64 {
	return percentile(et.Latencies, 0.50)
}

func (et *ExpertTelemetry) P99Latency() float64 {
	return percentile(et.Latencies, 0.99)
}

// RoutingSnapshot captures a point-in-time routing distribution.
type RoutingSnapshot struct {
	Timestamp    time.Time
	ExpertCounts []int64
	Entropy      float64
	CVSquared    float64
}

// DriftAlert signals routing pattern changes.
type DriftAlert struct {
	Timestamp time.Time
	AlertType string
	ExpertID  int
	OldValue  float64
	NewValue  float64
	Message   string
}

// TelemetryConfig configures the telemetry system.
type TelemetryConfig struct {
	NumExperts        int
	SnapshotInterval  time.Duration
	MaxLatencyHistory int
	MaxSnapshots      int
	DriftThreshold    float64
}

func DefaultTelemetryConfig(numExperts int) TelemetryConfig {
	return TelemetryConfig{
		NumExperts:        numExperts,
		SnapshotInterval:  5 * time.Second,
		MaxLatencyHistory: 1000,
		MaxSnapshots:      500,
		DriftThreshold:    0.3,
	}
}

// MoETelemetry is the main telemetry collection system.
type MoETelemetry struct {
	config    TelemetryConfig
	experts   []ExpertTelemetry
	snapshots []RoutingSnapshot
	alerts    []DriftAlert
	mu        sync.RWMutex
	startTime time.Time
}

func NewMoETelemetry(config TelemetryConfig) *MoETelemetry {
	experts := make([]ExpertTelemetry, config.NumExperts)
	for i := range experts {
		experts[i] = ExpertTelemetry{
			ExpertID:  i,
			Latencies: make([]float64, 0, config.MaxLatencyHistory),
		}
	}
	return &MoETelemetry{
		config:    config,
		experts:   experts,
		snapshots: make([]RoutingSnapshot, 0, config.MaxSnapshots),
		alerts:    make([]DriftAlert, 0),
		startTime: time.Now(),
	}
}

// RecordRouting records a batch of expert routing decisions.
func (t *MoETelemetry) RecordRouting(expertIndices []int, weights []float64, latencyMs float64) {
	t.mu.Lock()
	defer t.mu.Unlock()

	now := time.Now()
	for i, eid := range expertIndices {
		if eid < 0 || eid >= t.config.NumExperts {
			continue
		}
		et := &t.experts[eid]
		et.TokensRouted++
		if i < len(weights) {
			et.TotalWeight += weights[i]
		}
		et.Latencies = append(et.Latencies, latencyMs)
		if len(et.Latencies) > t.config.MaxLatencyHistory {
			et.Latencies = et.Latencies[1:]
		}
		et.LastActive = now
	}
}

// TakeSnapshot captures current routing distribution.
func (t *MoETelemetry) TakeSnapshot() RoutingSnapshot {
	t.mu.RLock()
	defer t.mu.RUnlock()

	counts := make([]int64, t.config.NumExperts)
	var total float64
	for i, et := range t.experts {
		counts[i] = et.TokensRouted
		total += float64(et.TokensRouted)
	}

	entropy := computeEntropy(counts, total)
	cv := computeCVSquared(counts, total)

	snap := RoutingSnapshot{
		Timestamp:    time.Now(),
		ExpertCounts: counts,
		Entropy:      entropy,
		CVSquared:    cv,
	}

	return snap
}

// SaveSnapshot takes and stores a snapshot.
func (t *MoETelemetry) SaveSnapshot() {
	snap := t.TakeSnapshot()
	t.mu.Lock()
	defer t.mu.Unlock()
	t.snapshots = append(t.snapshots, snap)
	if len(t.snapshots) > t.config.MaxSnapshots {
		t.snapshots = t.snapshots[1:]
	}
	// Check for drift
	if len(t.snapshots) >= 2 {
		t.detectDrift()
	}
}

// detectDrift compares last two snapshots for routing changes.
func (t *MoETelemetry) detectDrift() {
	n := len(t.snapshots)
	prev := t.snapshots[n-2]
	curr := t.snapshots[n-1]

	for i := 0; i < t.config.NumExperts; i++ {
		oldFrac := safeDiv(float64(prev.ExpertCounts[i]), sum64(prev.ExpertCounts))
		newFrac := safeDiv(float64(curr.ExpertCounts[i]), sum64(curr.ExpertCounts))
		drift := math.Abs(newFrac - oldFrac)

		if drift > t.config.DriftThreshold {
			alert := DriftAlert{
				Timestamp: time.Now(),
				AlertType: "EXPERT_DRIFT",
				ExpertID:  i,
				OldValue:  oldFrac,
				NewValue:  newFrac,
				Message:   "Significant routing shift detected",
			}
			t.alerts = append(t.alerts, alert)
		}
	}
}

// GetExpertStats returns telemetry for all experts.
func (t *MoETelemetry) GetExpertStats() []map[string]interface{} {
	t.mu.RLock()
	defer t.mu.RUnlock()

	stats := make([]map[string]interface{}, t.config.NumExperts)
	for i, et := range t.experts {
		stats[i] = map[string]interface{}{
			"expert_id":     et.ExpertID,
			"tokens_routed": et.TokensRouted,
			"avg_weight":    et.AvgWeight(),
			"p50_latency":   et.P50Latency(),
			"p99_latency":   et.P99Latency(),
			"error_count":   et.ErrorCount,
		}
	}
	return stats
}

// GetAlerts returns recent drift alerts.
func (t *MoETelemetry) GetAlerts() []DriftAlert {
	t.mu.RLock()
	defer t.mu.RUnlock()
	result := make([]DriftAlert, len(t.alerts))
	copy(result, t.alerts)
	return result
}

// Helper functions

func computeEntropy(counts []int64, total float64) float64 {
	if total == 0 {
		return 0
	}
	entropy := 0.0
	for _, c := range counts {
		p := float64(c) / total
		if p > 0 {
			entropy -= p * math.Log2(p)
		}
	}
	return entropy
}

func computeCVSquared(counts []int64, total float64) float64 {
	n := len(counts)
	if n == 0 || total == 0 {
		return 0
	}
	mean := total / float64(n)
	varSum := 0.0
	for _, c := range counts {
		diff := float64(c) - mean
		varSum += diff * diff
	}
	variance := varSum / float64(n)
	return variance / (mean*mean + 1e-8)
}

func percentile(data []float64, p float64) float64 {
	if len(data) == 0 {
		return 0
	}
	sorted := make([]float64, len(data))
	copy(sorted, data)
	sort.Float64s(sorted)
	idx := int(p * float64(len(sorted)-1))
	return sorted[idx]
}

func safeDiv(a, b float64) float64 {
	if b == 0 {
		return 0
	}
	return a / b
}

func sum64(arr []int64) float64 {
	s := float64(0)
	for _, v := range arr {
		s += float64(v)
	}
	return s
}

