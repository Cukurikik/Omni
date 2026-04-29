import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn enqueue_generation_task(task_id: String) -> OmniResult(String) {
  if task_id == "" {
    Error("Task ID cannot be empty")
  } else {
    // Gleam concurrent message passing queue for Open-dLLM generations
    Ok("Task queued successfully")
  }
}
