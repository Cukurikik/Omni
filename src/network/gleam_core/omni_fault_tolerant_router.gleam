// Omni Fault-Tolerant Router in Gleam
// Strict type-safe actor communication

import gleam/result
import gleam/list

pub type RouteError {
  EmptyPayload
  InvalidDestination
}

pub type Packet {
  Packet(destination: String, payload: BitArray)
}

pub fn route_packet(packet: Packet) -> Result(Bool, RouteError) {
  case packet.payload {
    <<>> -> Error(EmptyPayload)
    _ -> 
      case packet.destination {
        "" -> Error(InvalidDestination)
        _valid_dest -> {
          // Deterministic routing logic
          Ok(True)
        }
      }
  }
}
