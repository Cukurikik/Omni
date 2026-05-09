// OMNI Database — InfluxDB Flux Query
// Analyzes GPU telemetry data for thermal throttling

from(bucket: "omni_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "temperature_c")
  |> group(columns: ["node_id", "gpu_id"])
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  // Flag any GPU exceeding 85C for throttling logic
  |> map(fn: (r) => ({ r with thermal_warning: if r._value > 85.0 then true else false }))
  |> yield(name: "thermal_analysis")
