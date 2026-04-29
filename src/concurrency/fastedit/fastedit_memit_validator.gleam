import gleam/result
pub type OmniError { BufferFull  InvalidDim }
pub type OmniResult(t) { Ok(t)  Err(OmniError) }
pub fn validate_edit(hidden_dim: Int, num_edits: Int) -> OmniResult(Bool) {
  case hidden_dim > 16384 { True -> Err(InvalidDim) False ->
    case num_edits > 10000 { True -> Err(BufferFull) False -> Ok(True) }
  }
}
