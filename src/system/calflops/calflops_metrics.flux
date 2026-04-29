// Calflops Metrics Dashboard in Flux
from(bucket: "omni_metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "calflops")
  |> filter(fn: (r) => r["_field"] == "flops_per_second")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "mean_flops")
