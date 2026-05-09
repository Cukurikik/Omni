package network_gocore

import (
	"context"
	"sync"
	"time"
)

// ExpressivityMetricsTracker collects telemetry on LayerNorm expressivity
// across distributed transformer nodes in the OMNI Network.
type ExpressivityMetricsTracker struct {
	mu      sync.RWMutex
	metrics map[string]LayerMetric
}

type LayerMetric struct {
	LayerID          string
	AverageScore     float64
	ObservationCount uint64
	LastUpdated      time.Time
}

func NewExpressivityMetricsTracker() *ExpressivityMetricsTracker {
	return &ExpressivityMetricsTracker{
		metrics: make(map[string]LayerMetric),
	}
}

func (t *ExpressivityMetricsTracker) RecordScore(ctx context.Context, layerID string, score float64) {
	t.mu.Lock()
	defer t.mu.Unlock()

	metric, exists := t.metrics[layerID]
	if !exists {
		metric = LayerMetric{
			LayerID: layerID,
		}
	}

	// Moving average calculation
	total := metric.AverageScore*float64(metric.ObservationCount) + score
	metric.ObservationCount++
	metric.AverageScore = total / float64(metric.ObservationCount)
	metric.LastUpdated = time.Now()

	t.metrics[layerID] = metric
}

func (t *ExpressivityMetricsTracker) GetMetrics() map[string]LayerMetric {
	t.mu.RLock()
	defer t.mu.RUnlock()

	// Return a copy to avoid data races
	copyMap := make(map[string]LayerMetric)
	for k, v := range t.metrics {
		copyMap[k] = v
	}
	return copyMap
}

