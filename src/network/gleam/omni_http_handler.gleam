import gleam/http/request.{Request}
import gleam/http/response.{Response}
import gleam/bit_builder

pub fn handle_request(req: Request(BitString)) -> Response(bit_builder.BitBuilder) {
  case req.path {
    "/health" -> 
      response.new(200)
      |> response.set_body(bit_builder.from_string("{\"status\":\"healthy\",\"system\":\"omni\"}"))
      |> response.prepend_header("content-type", "application/json")
    
    "/metrics" ->
      response.new(200)
      |> response.set_body(bit_builder.from_string("omni_requests_total 1024"))
      |> response.prepend_header("content-type", "text/plain")

    _ ->
      response.new(404)
      |> response.set_body(bit_builder.from_string("Not Found in OMNI Gleam Router"))
  }
}
