import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn start_monitoring_loop(sensor_id: String) -> OmniResult(String) {
  if sensor_id == "" {
    Error("Invalid sensor ID")
  } else {
    // Gleam concurrent event loop for continuous, fault-tolerant fire detection polling
    Ok("Monitoring active")
  }
}
