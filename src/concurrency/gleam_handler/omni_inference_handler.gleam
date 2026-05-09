// @omni-layer Concurrency | @omni-lang Gleam | @omni-batch 18 | @omni-semester 16
// @omni-description Gleam type-safe transformer inference request handler
// with pattern matching, result types, and BEAM concurrency.

import gleam/list
import gleam/float
import gleam/int
import gleam/result
import gleam/string
import gleam/option.{type Option, None, Some}

pub type ModelType {
  TimeSeries
  NER
  VideoClassification
  ImageSegmentation
  TextClassification
}

pub type InferenceError {
  ModelNotFound(String)
  InvalidInput(String)
  InferenceFailed(String)
  RateLimitExceeded
}

pub type ModelConfig {
  ModelConfig(
    id: String,
    model_type: ModelType,
    version: String,
    d_model: Int,
    n_heads: Int,
    max_batch: Int,
  )
}

pub type InferenceRequest {
  InferenceRequest(
    model_id: String,
    input_tokens: List(Int),
    max_output: Int,
    temperature: Float,
  )
}

pub type InferenceResponse {
  InferenceResponse(
    request_id: String,
    output_tokens: List(Int),
    confidence: Float,
    model_version: String,
  )
}

pub fn create_model_config(
  id: String,
  model_type: ModelType,
) -> ModelConfig {
  ModelConfig(
    id: id,
    model_type: model_type,
    version: "1.0.0",
    d_model: 768,
    n_heads: 12,
    max_batch: 32,
  )
}

pub fn validate_request(
  req: InferenceRequest,
  config: ModelConfig,
) -> Result(InferenceRequest, InferenceError) {
  case list.length(req.input_tokens) {
    0 -> Error(InvalidInput("empty input"))
    n if n > 2048 -> Error(InvalidInput("input too long"))
    _ ->
      case req.max_output {
        m if m <= 0 -> Error(InvalidInput("invalid max_output"))
        m if m > 4096 -> Error(InvalidInput("max_output too large"))
        _ -> Ok(req)
      }
  }
}

pub fn route_inference(
  req: InferenceRequest,
  models: List(ModelConfig),
) -> Result(InferenceResponse, InferenceError) {
  case list.find(models, fn(m) { m.id == req.model_id }) {
    Ok(config) -> {
      use validated <- result.try(validate_request(req, config))
      execute_inference(validated, config)
    }
    Error(_) -> Error(ModelNotFound(req.model_id))
  }
}

fn execute_inference(
  req: InferenceRequest,
  config: ModelConfig,
) -> Result(InferenceResponse, InferenceError) {
  let output = generate_tokens(req.input_tokens, req.max_output)
  Ok(InferenceResponse(
    request_id: "req_" <> config.id <> "_" <> int.to_string(list.length(req.input_tokens)),
    output_tokens: output,
    confidence: 0.85,
    model_version: config.version,
  ))
}

fn generate_tokens(input: List(Int), max_len: Int) -> List(Int) {
  let seed = list.fold(input, 0, fn(acc, t) { acc + t })
  list.range(0, max_len - 1)
  |> list.map(fn(i) {
    let hash = { seed * 31 + i * 7 + 13 }
    int.absolute_value(hash) % 32000
  })
}
