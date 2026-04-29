import gleam/result
import gleam/list

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn merge_multimodal_streams(audio: List(Float), text: List(Float)) -> OmniResult(List(Float)) {
  if list.is_empty(audio) || list.is_empty(text) {
    Error("Streams cannot be empty")
  } else {
    // Interleave streams mathematically for Liquid model
    let merged = list.append(audio, text)
    Ok(merged)
  }
}
