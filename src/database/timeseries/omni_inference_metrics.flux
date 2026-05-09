// @omni-layer Database | @omni-lang Flux (InfluxDB) | @omni-batch 17
// @omni-description Time series analytics: Flux queries for inference
// latency monitoring, GPU utilization, and model throughput metrics.

// === 1. Inference Latency P50/P95/P99 over 1 hour ===
from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> quantile(q: 0.50, column: "_value", method: "exact_mean")
  |> yield(name: "p50")

from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> quantile(q: 0.95, column: "_value", method: "exact_mean")
  |> yield(name: "p95")

from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> quantile(q: 0.99, column: "_value", method: "exact_mean")
  |> yield(name: "p99")

// === 2. GPU Utilization heatmap (5-minute windows) ===
from(bucket: "omni_metrics")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "gpu_utilization")
  |> filter(fn: (r) => r._field == "percent")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> group(columns: ["gpu_id"])
  |> yield(name: "gpu_util")

// === 3. Model throughput (requests/sec) ===
from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_count")
  |> filter(fn: (r) => r._field == "count")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({r with _value: float(v: r._value) / 60.0}))
  |> group(columns: ["model_id"])
  |> yield(name: "throughput_rps")

// === 4. Anomaly detection: latency spikes ===
latency = from(bucket: "omni_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")

baseline = latency
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> mean()

latency
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> map(fn: (r) => ({r with is_anomaly: r._value > 3.0 * baseline._value}))
  |> filter(fn: (r) => r.is_anomaly == true)
  |> yield(name: "anomalies")

// === 5. Token throughput by model ===
from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "token_throughput")
  |> filter(fn: (r) => r._field == "tokens_per_sec")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> group(columns: ["model_id"])
  |> sort(columns: ["_time"], desc: false)
  |> yield(name: "token_throughput")

// === 6. Error rate monitoring ===
from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_errors")
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: true)
  |> fill(value: 0)
  |> yield(name: "error_rate")
