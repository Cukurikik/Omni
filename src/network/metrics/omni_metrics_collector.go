// omni_metrics_collector.go — Prometheus-Compatible Metrics Collector
// Inspired by: OMNI inference monitoring requirements
// Layer: Network / Go
//
// Lock-free metrics collection for model serving with histogram,
// counter, and gauge primitives exported via HTTP.

package metrics

import (
	"encoding/json"
	"fmt"
	"math"
	"net/http"
	"sort"
	"sync"
	"sync/atomic"
	"time"
)

type Counter struct {
	name  string
	value atomic.Int64
	help  string
}

func NewCounter(name, help string) *Counter {
	return &Counter{name: name, help: help}
}

func (c *Counter) Inc()         { c.value.Add(1) }
func (c *Counter) Add(v int64)  { c.value.Add(v) }
func (c *Counter) Value() int64 { return c.value.Load() }
func (c *Counter) Name() string { return c.name }
func (c *Counter) Help() string { return c.help }

type Gauge struct {
	name  string
	value atomic.Int64 // stores float64 as int64 bits
	help  string
}

func NewGauge(name, help string) *Gauge {
	return &Gauge{name: name, help: help}
}

func (g *Gauge) Set(v float64) {
	g.value.Store(int64(math.Float64bits(v)))
}

func (g *Gauge) Value() float64 {
	return math.Float64frombits(uint64(g.value.Load()))
}

func (g *Gauge) Inc()          { g.Set(g.Value() + 1) }
func (g *Gauge) Dec()          { g.Set(g.Value() - 1) }
func (g *Gauge) Add(v float64) { g.Set(g.Value() + v) }
func (g *Gauge) Name() string  { return g.name }
func (g *Gauge) Help() string  { return g.help }

type Histogram struct {
	name       string
	help       string
	boundaries []float64
	buckets    []atomic.Int64
	count      atomic.Int64
	sum        atomic.Int64 // float64 bits
	mu         sync.Mutex
}

func NewHistogram(name, help string, boundaries []float64) *Histogram {
	sort.Float64s(boundaries)
	h := &Histogram{
		name:       name,
		help:       help,
		boundaries: boundaries,
		buckets:    make([]atomic.Int64, len(boundaries)+1), // +1 for +Inf
	}
	return h
}

func (h *Histogram) Observe(v float64) {
	h.count.Add(1)

	// Atomically add to sum using CAS
	for {
		old := h.sum.Load()
		oldF := math.Float64frombits(uint64(old))
		newF := oldF + v
		newBits := int64(math.Float64bits(newF))
		if h.sum.CompareAndSwap(old, newBits) {
			break
		}
	}

	for i, boundary := range h.boundaries {
		if v <= boundary {
			h.buckets[i].Add(1)
			return
		}
	}
	h.buckets[len(h.boundaries)].Add(1) // +Inf bucket
}

func (h *Histogram) Count() int64 { return h.count.Load() }
func (h *Histogram) Sum() float64 { return math.Float64frombits(uint64(h.sum.Load())) }
func (h *Histogram) Mean() float64 {
	c := h.Count()
	if c == 0 {
		return 0
	}
	return h.Sum() / float64(c)
}
func (h *Histogram) Name() string { return h.name }
func (h *Histogram) Help() string { return h.help }

func (h *Histogram) Percentile(p float64) float64 {
	target := int64(float64(h.Count()) * p)
	var cumulative int64
	for i, boundary := range h.boundaries {
		cumulative += h.buckets[i].Load()
		if cumulative >= target {
			return boundary
		}
	}
	if len(h.boundaries) > 0 {
		return h.boundaries[len(h.boundaries)-1]
	}
	return 0
}

type MetricSnapshot struct {
	Name     string             `json:"name"`
	Type     string             `json:"type"`
	Help     string             `json:"help"`
	Value    interface{}        `json:"value"`
	Metadata map[string]float64 `json:"metadata,omitempty"`
}

type OmniMetricsCollector struct {
	mu         sync.RWMutex
	counters   map[string]*Counter
	gauges     map[string]*Gauge
	histograms map[string]*Histogram
	startTime  time.Time
}

func NewMetricsCollector() *OmniMetricsCollector {
	return &OmniMetricsCollector{
		counters:   make(map[string]*Counter),
		gauges:     make(map[string]*Gauge),
		histograms: make(map[string]*Histogram),
		startTime:  time.Now(),
	}
}

func (mc *OmniMetricsCollector) RegisterCounter(name, help string) *Counter {
	mc.mu.Lock()
	defer mc.mu.Unlock()
	c := NewCounter(name, help)
	mc.counters[name] = c
	return c
}

func (mc *OmniMetricsCollector) RegisterGauge(name, help string) *Gauge {
	mc.mu.Lock()
	defer mc.mu.Unlock()
	g := NewGauge(name, help)
	mc.gauges[name] = g
	return g
}

func (mc *OmniMetricsCollector) RegisterHistogram(name, help string, boundaries []float64) *Histogram {
	mc.mu.Lock()
	defer mc.mu.Unlock()
	h := NewHistogram(name, help, boundaries)
	mc.histograms[name] = h
	return h
}

func (mc *OmniMetricsCollector) Snapshot() []MetricSnapshot {
	mc.mu.RLock()
	defer mc.mu.RUnlock()

	var snapshots []MetricSnapshot

	for _, c := range mc.counters {
		snapshots = append(snapshots, MetricSnapshot{
			Name: c.Name(), Type: "counter", Help: c.Help(),
			Value: c.Value(),
		})
	}

	for _, g := range mc.gauges {
		snapshots = append(snapshots, MetricSnapshot{
			Name: g.Name(), Type: "gauge", Help: g.Help(),
			Value: g.Value(),
		})
	}

	for _, h := range mc.histograms {
		snapshots = append(snapshots, MetricSnapshot{
			Name: h.Name(), Type: "histogram", Help: h.Help(),
			Value: h.Mean(),
			Metadata: map[string]float64{
				"count": float64(h.Count()),
				"sum":   h.Sum(),
				"p50":   h.Percentile(0.5),
				"p95":   h.Percentile(0.95),
				"p99":   h.Percentile(0.99),
			},
		})
	}

	return snapshots
}

func (mc *OmniMetricsCollector) HandleMetrics(w http.ResponseWriter, r *http.Request) {
	snapshots := mc.Snapshot()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"metrics":    snapshots,
		"uptime_sec": time.Since(mc.startTime).Seconds(),
		"timestamp":  time.Now().UTC(),
	})
}

func (mc *OmniMetricsCollector) HandlePrometheus(w http.ResponseWriter, r *http.Request) {
	mc.mu.RLock()
	defer mc.mu.RUnlock()

	w.Header().Set("Content-Type", "text/plain")

	for _, c := range mc.counters {
		fmt.Fprintf(w, "# HELP %s %s\n", c.Name(), c.Help())
		fmt.Fprintf(w, "# TYPE %s counter\n", c.Name())
		fmt.Fprintf(w, "%s %d\n\n", c.Name(), c.Value())
	}

	for _, g := range mc.gauges {
		fmt.Fprintf(w, "# HELP %s %s\n", g.Name(), g.Help())
		fmt.Fprintf(w, "# TYPE %s gauge\n", g.Name())
		fmt.Fprintf(w, "%s %f\n\n", g.Name(), g.Value())
	}

	for _, h := range mc.histograms {
		fmt.Fprintf(w, "# HELP %s %s\n", h.Name(), h.Help())
		fmt.Fprintf(w, "# TYPE %s histogram\n", h.Name())
		fmt.Fprintf(w, "%s_count %d\n", h.Name(), h.Count())
		fmt.Fprintf(w, "%s_sum %f\n\n", h.Name(), h.Sum())
	}
}
