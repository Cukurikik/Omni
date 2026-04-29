// OMNI Concurrency Layer - Gleam Message Router
import gleam/erlang/process.{type Subject}
import gleam/result

pub type OmniMessage {
  RouteTask(id: String, payload: String)
  SystemHalt
}

pub type RouterError {
  InvalidPayload
  NodeOffline
}

pub fn route_message(msg: OmniMessage) -> Result(String, RouterError) {
  case msg {
    RouteTask(id, payload) -> {
      // In a real OMNI system, this delegates to the BEAM VM actor model
      Ok("Task " <> id <> " routed successfully")
    }
    SystemHalt -> {
      Error(NodeOffline)
    }
  }
}
