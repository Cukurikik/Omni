import gleam/string
import gleam/list

pub fn parse_security_log(log: String) -> Result(String, String) {
  let parts = string.split(log, on: " ")
  case list.length(parts) > 3 {
    True -> Ok("Valid log entry")
    False -> Error("Malformed security log")
  }
}
