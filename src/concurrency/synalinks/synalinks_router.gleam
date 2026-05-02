// @omni-domain Concurrency Layer (Synalinks)
// @omni-source various/synalinks
// @omni-description Synalinks Router mimicking concurrent API routing.
// @omni-requirement zero-mock, monadic-error

import gleam/map
import gleam/result

pub type RouteError {
  RouteNotFound
  InvalidPayload
}

pub type Router {
  Router(routes: map.Map(String, String))
}

pub fn new_router() -> Router {
  Router(map.new())
}

pub fn add_route(router: Router, path: String, handler_id: String) -> Result(Router, RouteError) {
  case path {
    "" -> Error(InvalidPayload)
    _ -> Ok(Router(map.insert(router.routes, path, handler_id)))
  }
}

pub fn route_request(router: Router, path: String) -> Result(String, RouteError) {
  case map.get(router.routes, path) {
    Ok(handler) -> Ok(handler)
    Error(_) -> Error(RouteNotFound)
  }
}
