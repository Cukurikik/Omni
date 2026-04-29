// Omni Attention Sink Metrics (Flux)
// Database Layer: Time-series query for attention sink magnitude tracking.
// Ref: sail-sg/Attention-Sink

from(bucket: "omni_telemetry")
  |> range(start: -6h)
  |> filter(fn: (r) => r["_measurement"] == "attention_sink")
  |> filter(fn: (r) => r["_field"] == "sink_magnitude")
  |> aggregateWindow(every: 5m, fn: max, createEmpty: false)
  |> yield(name: "peak_sink_values")
