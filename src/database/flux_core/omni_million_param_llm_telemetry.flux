// Omni Million Parameter LLM Telemetry (Flux / InfluxDB)
// Deterministic time-series aggregation for CUDA kernel latency

import "math"

from(bucket: "omni_production")
  |> range(start: -24h)
  |> filter(fn: (r) => r["_measurement"] == "cuda_kernel_latency")
  |> filter(fn: (r) => r["layer"] == "hardware_acceleration")
  |> filter(fn: (r) => r["kernel"] == "omni_llm_ffn_kernel")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> yield(name: "mean_ffn_latency")
