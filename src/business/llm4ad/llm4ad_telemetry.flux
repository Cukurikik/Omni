// Autonomous Driving telemetry influx query
// Flux language for LLM4AD

// Bound: Range strictly limited to last 1 hour to prevent massive data pull
from(bucket: "llm4ad_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r["_measurement"] == "vehicle_state")
  |> filter(fn: (r) => r["_field"] == "velocity" or r["_field"] == "steering_angle")
  |> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  |> yield(name: "mean")
