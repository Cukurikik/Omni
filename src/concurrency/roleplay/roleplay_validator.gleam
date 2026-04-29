import gleam/result

pub type OmniResult(a) = Result(a, String)

pub fn validate_role_config(persona_name: String, traits: List(String)) -> OmniResult(Int) {
  case persona_name {
    "" -> Error("Empty persona name")
    _ -> case traits {
      [] -> Error("No traits specified")
      t -> case list.length(t) > 50 {
        True -> Error("Traits exceed 50")
        False -> Ok(list.length(t))
      }
    }
  }
}
