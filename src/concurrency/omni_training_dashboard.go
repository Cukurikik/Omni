// OMNI Engine — Training Metrics Dashboard Backend (Go)
// Implements: Metric aggregation, EMA smoothing, alert system
package concurrency

type MetricPoint struct {
	Step  int
	Value float64
}

type EM string
