// moe_token_drop_metrics.go — Network / Telemetry
// Layer: Network / Observability — Prometheus Token Drop Exporter
//
// MoE models intentionally drop tokens when experts are overloaded.
// This exporter tracks those drops as Prometheus metrics, allowing SREs
// to visualize if the cluster's capacity factor is tuned incorrectly.

package network_moe

import (
	"fmt"
	"sync/atomic"
	"time"
)

// Mock Prometheus interfaces for Zero-Mock compilation
type Counter struct {
	val uint64
}

func (c *Counter) Inc(amount uint64) { atomic.AddUint64(&c.val, amount) }
func (c *Counter) Get() uint64       { return atomic.LoadUint64(&c.val) }

var (
	TotalTokensRouted  = &Counter{}
	TotalTokensDropped = &Counter{}
)

// MetricExporter runs as a background goroutine
type MetricExporter struct {
	pollInterval time.Duration
}

func NewMetricExporter() *MetricExporter {
	return &MetricExporter{
		pollInterval: 5 * time.Second,
	}
}

// RecordRoutingEvent is called by the API Gateway after the Rust capacity manager returns
func (m *MetricExporter) RecordRoutingEvent(accepted int, dropped int) {
	TotalTokensRouted.Inc(uint64(accepted + dropped))
	TotalTokensDropped.Inc(uint64(dropped))
}

// Start begins the Prometheus logging loop
func (m *MetricExporter) Start() {
	go func() {
		fmt.Println("[MoE Metrics] Started Token Drop Prometheus Exporter.")
		for {
			time.Sleep(m.pollInterval)
			routed := TotalTokensRouted.Get()
			dropped := TotalTokensDropped.Get()

			var dropRate float64 = 0.0
			if routed > 0 {
				dropRate = (float64(dropped) / float64(routed)) * 100.0
			}

			if dropRate > 5.0 {
				fmt.Printf("[MoE Metrics ALERT] High Token Drop Rate: %.2f%% (%d / %d)\n", dropRate, dropped, routed)
			}
		}
	}()
}

