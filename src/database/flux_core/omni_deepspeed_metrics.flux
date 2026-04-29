// Omni DeepSpeed Metrics (Flux)
// Database Layer: Time-series query for tracking memory allocations per GPU.

from(bucket: "omni_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "deepspeed_allocator")
  |> filter(fn: (r) => r["_field"] == "allocated_bytes")
  |> filter(fn: (r) => r["gpu_id"] == "0" or r["gpu_id"] == "1")
  |> aggregateWindow(every: 1m, fn: max, createEmpty: false)
  |> yield(name: "peak_memory_usage")
