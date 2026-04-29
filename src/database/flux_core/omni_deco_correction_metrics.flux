// Omni DeCo Correction Metrics (Flux)
// Database Layer: Time-series correction rate monitoring.
// Ref: zjunlp/Deco — ICLR 2025
from(bucket: "omni_telemetry")
  |> range(start: -6h)
  |> filter(fn: (r) => r["_measurement"] == "deco_correction")
  |> filter(fn: (r) => r["_field"] == "correction_rate")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> yield(name: "avg_correction_rate")
