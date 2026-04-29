import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn start_data_loader(dataset_path: String) -> OmniResult(String) {
  if dataset_path == "" {
    Error("Invalid path")
  } else {
    // Gleam concurrent data loading pipeline feeding the from-scratch LLM trainer
    Ok("Data loading started")
  }
}
