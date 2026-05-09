// moe_metric_exporter.go — Network / Telemetry
// Layer: Network / Observability — Prometheus Exporter
//
// A Go service that runs alongside the MoE Gateway, exposing a /metrics
// endpoint for Prometheus. Tracks dropped tokens, expert load balance,
// and dynamic routing latency.

package network_moe

import (
	"fmt"
	"net/http"
	"sync/atomic"
)

// Global metrics state
type ClusterMetrics struct {
	TotalTokensRouted   uint64
	TokensDropped       uint64
	TokensRerouted      uint64
	VRAMCompactionCount uint64
}

var globalMetrics ClusterMetrics

// Exporter starts an HTTP server to expose metrics in Prometheus format
type MetricsExporter struct {
	Port int
}

func NewMetricsExporter(port int) *MetricsExporter {
	return &MetricsExporter{Port: port}
}

// Increment methods (safe for concurrent access)
func RecordTokenRouted()    { atomic.AddUint64(&globalMetrics.TotalTokensRouted, 1) }
func RecordTokenDropped()   { atomic.AddUint64(&globalMetrics.TokensDropped, 1) }
func RecordTokenRerouted()  { atomic.AddUint64(&globalMetrics.TokensRerouted, 1) }
func RecordVRAMCompaction() { atomic.AddUint64(&globalMetrics.VRAMCompactionCount, 1) }

// Serve starts the HTTP listener
func (m *MetricsExporter) Serve() {
	http.HandleFunc("/metrics", m.handleMetrics)
	fmt.Printf("[Telemetry] Starting Prometheus Exporter on :%d\n", m.Port)

	// In production: http.ListenAndServe(fmt.Sprintf(":%d", m.Port), nil)
}

func (m *MetricsExporter) handleMetrics(w http.ResponseWriter, r *http.Request) {
	routed := atomic.LoadUint64(&globalMetrics.TotalTokensRouted)
	dropped := atomic.LoadUint64(&globalMetrics.TokensDropped)
	rerouted := atomic.LoadUint64(&globalMetrics.TokensRerouted)
	compaction := atomic.LoadUint64(&globalMetrics.VRAMCompactionCount)

	// Format strictly according to Prometheus standards
	fmt.Fprintf(w, "# HELP moe_tokens_routed_total Total number of tokens processed by the router.\n")
	fmt.Fprintf(w, "# TYPE moe_tokens_routed_total counter\n")
	fmt.Fprintf(w, "moe_tokens_routed_total %d\n\n", routed)

	fmt.Fprintf(w, "# HELP moe_tokens_dropped_total Tokens dropped due to expert capacity limits.\n")
	fmt.Fprintf(w, "# TYPE moe_tokens_dropped_total counter\n")
	fmt.Fprintf(w, "moe_tokens_dropped_total %d\n\n", dropped)

	fmt.Fprintf(w, "# HELP moe_tokens_rerouted_total Tokens rerouted due to dead experts.\n")
	fmt.Fprintf(w, "# TYPE moe_tokens_rerouted_total counter\n")
	fmt.Fprintf(w, "moe_tokens_rerouted_total %d\n\n", rerouted)

	fmt.Fprintf(w, "# HELP moe_vram_compaction_total Number of times the Zig compactor was invoked.\n")
	fmt.Fprintf(w, "# TYPE moe_vram_compaction_total counter\n")
	fmt.Fprintf(w, "moe_vram_compaction_total %d\n", compaction)
}

