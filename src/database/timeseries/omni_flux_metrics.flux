// OMNI Database & Query Layer: Flux (InfluxDB)
// Real-time latency monitoring of transformer heads and generation throughput

import "math"
import "experimental"

// Calculate rolling 99th percentile latency of the OMNI execution engine
data = from(bucket: "omni_telemetry")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "inference_latency")
  |> filter(fn: (r) => r._field == "duration_ms")
  |> filter(fn: (r) => r.layer == "transformer_attention")

p99_latency = data
  |> aggregateWindow(every: 1m, fn: (column, tables=<-) => 
      tables |> quantile(q: 0.99, method: "exact_selector")
  )
  |> yield(name: "p99_latency")

// Detect anomalies where latency suddenly spikes 3x above moving average
moving_avg = data
  |> movingAverage(n: 5)

join(tables: {current: data, avg: moving_avg}, on: ["_time", "_measurement", "_field", "layer"])
  |> map(fn: (r) => ({ r with 
      is_anomaly: r._value_current > (r._value_avg * 3.0) 
  }))
  |> filter(fn: (r) => r.is_anomaly == true)
  |> yield(name: "latency_anomalies")
