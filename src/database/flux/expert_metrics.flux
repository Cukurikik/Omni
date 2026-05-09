// OMNI Framework - Expert Metrics Telemetry (Flux for InfluxDB)
// Analyzes real-time telemetry from the MoE cluster to identify 
// expert imbalances and hardware thermal throttling over the last hour.

import "math"
import "experimental"

// 1. Calculate Average Load Per Expert
expert_load = from(bucket: "omni_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "moe_routing" and r._field == "tokens_processed")
  |> group(columns: ["expert_id", "node_id"])
  |> aggregateWindow(every: 1m, fn: sum, createEmpty: false)
  |> yield(name: "Tokens Per Minute Per Expert")

// 2. Identify Thermally Throttled Nodes Hosting Experts
thermal_throttling = from(bucket: "omni_hardware")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "gpu_metrics" and r._field == "temperature")
  |> filter(fn: (r) => r._value > 85.0) // Flag GPUs > 85°C
  |> yield(name: "Throttled GPUs")

// 3. Detect Routing Skew (Standard Deviation across experts)
skew_analysis = expert_load
  |> group(columns: ["_time"])
  |> stddev()
  |> map(fn: (r) => ({ r with _value: if r._value > 10000.0 then "CRITICAL_SKEW" else "NORMAL" }))
  |> yield(name: "Routing Skew Alarm")
