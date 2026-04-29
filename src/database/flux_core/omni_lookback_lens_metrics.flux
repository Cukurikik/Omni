// Omni Lookback Lens Metrics (Flux)
// Database Layer: Time-series lookback ratio monitoring.
// Ref: voidism/Lookback-Lens
from(bucket: "omni_telemetry")
  |> range(start: -4h)
  |> filter(fn: (r) => r["_measurement"] == "lookback_lens")
  |> filter(fn: (r) => r["_field"] == "lookback_ratio")
  |> aggregateWindow(every: 2m, fn: mean, createEmpty: false)
  |> yield(name: "avg_lookback_ratio")
