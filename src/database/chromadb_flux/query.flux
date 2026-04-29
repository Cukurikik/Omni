from(bucket: "chromadb_telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "embedding_latency")
  |> mean()
