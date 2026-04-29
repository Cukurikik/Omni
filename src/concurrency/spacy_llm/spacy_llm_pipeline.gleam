import gleam/result

pub type OmniError { PipelineFull  InvalidTask }
pub type OmniResult(t) { Ok(t)  Err(OmniError) }

pub fn dispatch(queue_depth: Int, text_len: Int) -> OmniResult(String) {
  case queue_depth >= 5000 {
    True -> Err(PipelineFull)
    False -> case text_len > 100_000 {
      True -> Err(InvalidTask)
      False -> Ok("dispatched")
    }
  }
}
