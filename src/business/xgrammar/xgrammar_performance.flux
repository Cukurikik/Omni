// XGrammar latency metrics
// Flux language

from(bucket: "xgrammar_metrics")
  |> range(start: -5m)
  |> filter(fn: (r) => r["_measurement"] == "parse_latency")
  |> aggregateWindow(every: 1m, fn: max, createEmpty: false)
  |> yield(name: "max_latency")
