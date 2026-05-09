// @omni-layer Database | @omni-lang Flux | @omni-batch 18 | @omni-semester 16
// @omni-description Flux InfluxDB queries for transformer inference monitoring:
// latency percentiles, throughput, GPU utilization, and model health.

// === Inference Latency P50/P95/P99 ===
inference_latency_percentiles = from(bucket: "omni_transformers")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> quantile(q: 0.50, column: "_value", method: "exact_mean")
  |> yield(name: "p50")

inference_p95 = from(bucket: "omni_transformers")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> quantile(q: 0.95, column: "_value", method: "exact_mean")
  |> yield(name: "p95")

// === Throughput (tokens/sec) ===
throughput = from(bucket: "omni_transformers")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference_throughput")
  |> filter(fn: (r) => r._field == "tokens_per_second")
  |> group(columns: ["model_id"])
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "throughput")

// === GPU Utilization ===
gpu_util = from(bucket: "omni_transformers")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics")
  |> filter(fn: (r) => r._field == "utilization_percent")
  |> group(columns: ["gpu_id", "model_id"])
  |> aggregateWindow(every: 30s, fn: mean, createEmpty: false)
  |> yield(name: "gpu_utilization")

// === Model Health Score ===
model_health = from(bucket: "omni_transformers")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> reduce(
      fn: (r, accumulator) => ({
        count: accumulator.count + 1.0,
        errors: if r._value > 5000.0 then accumulator.errors + 1.0 else accumulator.errors,
        sum: accumulator.sum + r._value
      }),
      identity: {count: 0.0, errors: 0.0, sum: 0.0}
    )
  |> map(fn: (r) => ({
      r with
      health_score: (1.0 - r.errors / if r.count > 0.0 then r.count else 1.0) * 100.0,
      avg_latency: r.sum / if r.count > 0.0 then r.count else 1.0
    }))
  |> yield(name: "health")

// === Weight Sync Throughput ===
weight_sync = from(bucket: "omni_transformers")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "weight_sync")
  |> filter(fn: (r) => r._field == "bytes_transferred")
  |> group(columns: ["cluster_id"])
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({r with throughput_gbps: float(v: r._value) / 1000000000.0 / 60.0}))
  |> yield(name: "weight_sync_throughput")
