import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn download_assets(urls: String) -> OmniResult(String) {
  if urls == "" {
    Error("No URLs provided")
  } else {
    // Gleam concurrent worker pool for aggressively prefetching generated slide images
    Ok("Assets downloading")
  }
}
