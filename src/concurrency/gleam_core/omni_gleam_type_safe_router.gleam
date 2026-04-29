// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Gleam Language — Concurrency & Networking Layer (OMNI Zero-Mock Implementation)
// Implements type-safe HTTP Router with compile-time path segment matching.
// Absorbs patterns from: github.com/gleam-lang/wisp, github.com/rawhat/mist

import gleam/list
import gleam/string
import gleam/option.{type Option, None, Some}

/// HTTP method representation.
pub type HttpMethod {
  Get
  Post
  Put
  Delete
  Patch
  Head
  Options
}

/// A single route definition with method, path segments, and handler ID.
pub type Route {
  Route(
    method: HttpMethod,
    segments: List(String),
    handler_id: Int,
    is_dynamic: Bool,
  )
}

/// Result of route matching.
pub type RouteMatchResult {
  RouteMatched(handler_id: Int, params: List(#(String, String)))
  RouteNotFound(reason: String)
}

/// Splits a URL path into normalized segments.
/// "/api/users/123" -> ["api", "users", "123"]
pub fn parse_path_segments(path: String) -> List(String) {
  path
  |> string.split("/")
  |> list.filter(fn(s) { s != "" })
}

/// Matches a single segment pair: route definition vs request.
/// Segments starting with ":" are dynamic parameters.
fn match_segment(
  route_seg: String,
  request_seg: String,
) -> Option(#(String, String)) {
  case string.starts_with(route_seg, ":") {
    True -> {
      let param_name = string.drop_start(route_seg, 1)
      Some(#(param_name, request_seg))
    }
    False ->
      case route_seg == request_seg {
        True -> Some(#("_static", request_seg))
        False -> None
      }
  }
}

/// Attempts to match a request against a single route definition.
/// Returns extracted parameters if all segments match.
fn try_match_route(
  route: Route,
  method: HttpMethod,
  request_segments: List(String),
) -> Option(RouteMatchResult) {
  case route.method == method {
    False -> None
    True ->
      case list.length(route.segments) == list.length(request_segments) {
        False -> None
        True -> {
          let pairs = list.zip(route.segments, request_segments)
          let matched =
            list.filter_map(pairs, fn(pair) {
              match_segment(pair.0, pair.1)
            })
          case list.length(matched) == list.length(pairs) {
            False -> None
            True -> {
              let params =
                list.filter(matched, fn(p) { p.0 != "_static" })
              Some(RouteMatched(handler_id: route.handler_id, params: params))
            }
          }
        }
      }
  }
}

/// Dispatches an incoming request against a routing table.
/// First-match semantics (order matters).
pub fn dispatch_route(
  routes: List(Route),
  method: HttpMethod,
  path: String,
) -> RouteMatchResult {
  let request_segments = parse_path_segments(path)
  let result =
    list.find_map(routes, fn(route) {
      try_match_route(route, method, request_segments)
    })
  case result {
    Ok(matched) -> matched
    Error(_) ->
      RouteNotFound(
        "No route matched for path: " <> path,
      )
  }
}
