// Omni Telemetry Query in Flux (InfluxDB)
// Deterministic time-series aggregation for system metrics

import "math"

from(bucket: "omni_production")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "engine_latency")
  |> filter(fn: (r) => r["layer"] == "system" or r["layer"] == "network")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "mean_latency")
