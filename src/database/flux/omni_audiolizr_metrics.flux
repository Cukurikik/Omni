// OMNI Framework - Flux Query for Audiolizr Latency Metrics
// Queries InfluxDB to monitor BentoML transcription speeds

from(bucket: "omni_production")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "audiolizr_inference")
  |> filter(fn: (r) => r["_field"] == "latency_ms")
  |> filter(fn: (r) => r["model"] == "whisper-large-v2")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> yield(name: "average_latency_5m")
