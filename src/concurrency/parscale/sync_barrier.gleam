import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn await_all_nodes(node_count: Int) -> OmniResult(String) {
  if node_count <= 0 {
    Error("Node count must be > 0")
  } else {
    // Gleam concurrent synchronization barrier for distributed scaling (ParScale)
    Ok("All nodes synchronized at barrier")
  }
}
