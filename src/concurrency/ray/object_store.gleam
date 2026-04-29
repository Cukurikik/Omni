import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn put_object(object_id: String, data_size: Int) -> OmniResult(String) {
  if data_size <= 0 {
    Error("Data size must be positive")
  } else {
    // Gleam concurrent distributed object store management for Ray
    Ok("Object stored in plasma")
  }
}
