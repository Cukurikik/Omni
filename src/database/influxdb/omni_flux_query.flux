// InfluxDB Flux script for OMNI telemetry
// Aggregates GPU temperatures over the last 15 minutes

from(bucket: "omni_telemetry")
  |> range(start: -15m)
  |> filter(fn: (r) => r["_measurement"] == "gpu_metrics")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "mean_temperature")
