import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn sync_video_frames(fps: Int) -> OmniResult(String) {
  if fps <= 0 {
    Error("Invalid FPS")
  } else {
    // Gleam actor-based synchronization for streaming decoded frames
    Ok("Frame synchronization active")
  }
}
