// RAGHub retrieval endpoint router.
// Gleam actor based robust routing.

import gleam/erlang/process
import gleam/result

pub type OmniError {
  RateLimitExceeded
  RouterOffline
}

pub type OmniResult(t) {
  Ok(t)
  Err(OmniError)
}

pub type RAGRequest {
  Query(payload: String, namespace: String)
}

pub type RouterMessage {
  Dispatch(req: RAGRequest, reply_channel: process.Subject(OmniResult(String)))
}

pub fn start_router() -> process.Subject(RouterMessage) {
  process.start(fn() { router_loop(0) }, True)
}

fn router_loop(request_count: Int) {
  let max_requests = 100_000

  let msg = process.receive_any(1000)
  
  // Actor state tracking for rate limiting
  case request_count >= max_requests {
    True -> {
      // Reject and cool down
      router_loop(0) 
    }
    False -> {
      // In a real Gleam app, we parse the message dynamically
      router_loop(request_count + 1)
    }
  }
}
