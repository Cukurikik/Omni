// @omni-domain Business Layer (CalFLOPs Metrics)
// @omni-source MrYxJ/calculate-flops.pytorch
// @omni-description CalFLOPs Metrics mimicking InfluxDB line protocol in Flux.
// @omni-requirement zero-mock, monadic-error

from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "calflops" and r._field == "total_flops")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> yield(name: "mean_flops")

from(bucket: "omni_metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "calflops" and r._field == "inference_latency_ms")
  |> aggregateWindow(every: 1h, fn: max, createEmpty: false)
  |> yield(name: "peak_latency")
