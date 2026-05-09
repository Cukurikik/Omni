// OMNI Framework - Gopilot Gateway (Gleam)
// Safe, purely functional routing for the Gopilot code generation LLM requests.

import gleam/http/request.{Request}
import gleam/http/response.{Response}
import gleam/string

pub type ProxyError {
  Unauthorized
  BadPayload
}

pub fn handle_gopilot_request(req: Request(String), api_key: String) -> Result(Response(String), ProxyError) {
  // Validate API key authorization
  let is_auth = case request.get_header(req, "authorization") {
    Ok(val) -> val == string.append("Bearer ", api_key)
    Error(_) -> False
  }

  case is_auth {
    False -> Error(Unauthorized)
    True -> {
      // In a real framework, this forwards to the Go backend.
      // Here we simulate the proxy returning 202 Accepted.
      Ok(
        response.new(202)
        |> response.set_body("{\"status\": \"forwarded to gopilot worker\"}")
      )
    }
  }
}
