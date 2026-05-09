-- OMNI Database Layer — InfluxDB Flux Queries for Inference Metrics
-- Time-series analytics for model performance monitoring.

// Query: Average inference latency per model (last hour)
from(bucket: "omni-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> mean()
  |> rename(columns: {_value: "avg_latency_ms"})
  |> sort(columns: ["avg_latency_ms"])

// Query: Request rate per minute per model
from(bucket: "omni-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "request_count")
  |> group(columns: ["model_id"])
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> rename(columns: {_value: "requests_per_minute"})

// Query: P99 latency (15-minute windows)
from(bucket: "omni-metrics")
  |> range(start: -6h)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> aggregateWindow(every: 15m, fn: (column, tables=<-) => tables |> quantile(q: 0.99, column: column))
  |> rename(columns: {_value: "p99_latency_ms"})

// Query: Error rate percentage
error_count = from(bucket: "omni-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "error_count")
  |> group(columns: ["model_id"])
  |> sum()

total_count = from(bucket: "omni-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "request_count")
  |> group(columns: ["model_id"])
  |> sum()

join(tables: {errors: error_count, total: total_count}, on: ["model_id"])
  |> map(fn: (r) => ({r with error_rate: float(v: r._value_errors) / float(v: r._value_total) * 100.0}))

// Query: GPU utilization over time
from(bucket: "omni-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "gpu" and r._field == "utilization_percent")
  |> group(columns: ["gpu_id"])
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)

// Query: Tokens per second throughput
from(bucket: "omni-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "tokens_generated")
  |> group(columns: ["model_id"])
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({r with tokens_per_second: float(v: r._value) / 60.0}))

// Alert: Latency exceeds SLA threshold
from(bucket: "omni-metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r._measurement == "inference" and r._field == "latency_ms")
  |> group(columns: ["model_id"])
  |> mean()
  |> filter(fn: (r) => r._value > 500.0)
  |> map(fn: (r) => ({r with alert: "LATENCY_SLA_BREACH", severity: "critical"}))
