// OMNI Concurrency Layer — Gleam Type-Safe Inference Router
// Gleam's type system ensures safe message passing for inference requests.

import gleam/int
import gleam/float
import gleam/list
import gleam/option.{type Option, None, Some}
import gleam/result
import gleam/string

/// Model inference request
pub type InferenceRequest {
  InferenceRequest(
    id: String,
    prompt: String,
    max_tokens: Int,
    temperature: Float,
    top_p: Float,
    stream: Bool,
  )
}

/// Model inference response
pub type InferenceResponse {
  InferenceResponse(
    request_id: String,
    generated_text: String,
    tokens_generated: Int,
    latency_ms: Float,
    finish_reason: FinishReason,
  )
}

pub type FinishReason {
  Stop
  MaxTokens
  Error(String)
}

/// Worker state
pub type WorkerState {
  WorkerState(
    id: Int,
    model_loaded: Bool,
    requests_served: Int,
    total_latency_ms: Float,
  )
}

/// Create a new worker
pub fn new_worker(id: Int) -> WorkerState {
  WorkerState(id: id, model_loaded: False, requests_served: 0, total_latency_ms: 0.0)
}

/// Load model into worker
pub fn load_model(state: WorkerState) -> WorkerState {
  WorkerState(..state, model_loaded: True)
}

/// Process an inference request
pub fn process_request(
  state: WorkerState,
  request: InferenceRequest,
) -> Result(#(WorkerState, InferenceResponse), String) {
  case state.model_loaded {
    False -> result.Error("Model not loaded on worker " <> int.to_string(state.id))
    True -> {
      let response = InferenceResponse(
        request_id: request.id,
        generated_text: "Response for: " <> string.slice(request.prompt, 0, 50),
        tokens_generated: request.max_tokens,
        latency_ms: 42.5,
        finish_reason: Stop,
      )
      let new_state = WorkerState(
        ..state,
        requests_served: state.requests_served + 1,
        total_latency_ms: state.total_latency_ms +. 42.5,
      )
      Ok(#(new_state, response))
    }
  }
}

/// Get average latency for a worker
pub fn avg_latency(state: WorkerState) -> Float {
  case state.requests_served {
    0 -> 0.0
    n -> state.total_latency_ms /. int.to_float(n)
  }
}

/// Router that distributes requests across workers
pub type Router {
  Router(
    workers: List(WorkerState),
    current_index: Int,
    total_routed: Int,
  )
}

pub fn new_router(num_workers: Int) -> Router {
  let workers = list.range(1, num_workers)
    |> list.map(fn(i) { new_worker(i) |> load_model })
  Router(workers: workers, current_index: 0, total_routed: 0)
}

/// Route a request to the next available worker
pub fn route(
  router: Router,
  request: InferenceRequest,
) -> Result(#(Router, InferenceResponse), String) {
  case list.at(router.workers, router.current_index) {
    result.Error(_) -> result.Error("No workers available")
    Ok(worker) -> {
      case process_request(worker, request) {
        result.Error(e) -> result.Error(e)
        Ok(#(new_worker, response)) -> {
          let new_workers = list.index_map(router.workers, fn(w, i) {
            case i == router.current_index {
              True -> new_worker
              False -> w
            }
          })
          let next_idx = { router.current_index + 1 } % list.length(router.workers)
          let new_router = Router(
            workers: new_workers,
            current_index: next_idx,
            total_routed: router.total_routed + 1,
          )
          Ok(#(new_router, response))
        }
      }
    }
  }
}
