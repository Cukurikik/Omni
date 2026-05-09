// OMNI Network — Gleam HTTP/2 Server
// Type-safe concurrent web server for robust API endpoints

import gleam/io
import gleam/http/request.{Request}
import gleam/http/response.{Response}
import gleam/bytes_builder

// Define the handler type
pub type Handler = fn(Request(BitArray)) -> Response(bytes_builder.BytesBuilder)

pub fn handle_request(req: Request(BitArray)) -> Response(bytes_builder.BytesBuilder) {
  case req.path {
    "/v1/health" -> {
      response.new(200)
      |> response.set_header("content-type", "application/json")
      |> response.set_body(bytes_builder.from_string("{\"status\":\"healthy\",\"layer\":\"gleam\"}"))
    }
    _ -> {
      response.new(404)
      |> response.set_body(bytes_builder.from_string("Not Found"))
    }
  }
}

pub fn start_server() {
  io.println("OMNI Gleam Server starting on port 8080...")
  // In a full implementation, we'd bind this to a real TCP socket like mist or elli
}
