// OMNI Framework - Gleam Router for text-generator.io APIs
import gleam/http/request
import gleam/http/response
import gleam/bit_builder

pub fn handle_request(req: request.Request(BitString)) -> response.Response(bit_builder.BitBuilder) {
  case req.path_segments(req) {
    ["api", "v1", "generate"] -> {
      response.new(200)
      |> response.set_body(bit_builder.from_string("{\"status\": \"generating\", \"model\": \"omni-vision-llm\"}"))
    }
    ["api", "v1", "tts"] -> {
      response.new(200)
      |> response.set_body(bit_builder.from_string("{\"status\": \"tts_processing\"}"))
    }
    _ -> {
      response.new(404)
      |> response.set_body(bit_builder.from_string("{\"error\": \"not_found\"}"))
    }
  }
}
