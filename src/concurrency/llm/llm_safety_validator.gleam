import gleam/result

pub type OmniResult(a) = Result(a, String)

pub fn validate_safety_check(input_text: String, max_len: Int) -> OmniResult(Int) {
  case string.length(input_text) {
    0 -> Error("Empty input")
    n -> case n > max_len {
      True -> Error("Input exceeds max length")
      False -> Ok(n)
    }
  }
}
