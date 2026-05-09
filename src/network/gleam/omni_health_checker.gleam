// OMNI Network — Gleam Type-Safe Model Health Checker
// Periodic health probing for inference cluster nodes.

import gleam/http
import gleam/json
import gleam/int
import gleam/float
import gleam/list
import gleam/option.{type Option, Some, None}

pub type NodeStatus {
  Healthy
  Degraded
  Unreachable
}

pub type NodeHealth {
  NodeHealth(
    node_id: String,
    endpoint: String,
    status: NodeStatus,
    latency_ms: Float,
    gpu_utilization: Float,
    memory_used_pct: Float,
    active_requests: Int,
    last_check: Int,
  )
}

pub type ClusterHealth {
  ClusterHealth(
    nodes: List(NodeHealth),
    healthy_count: Int,
    total_count: Int,
    avg_latency_ms: Float,
  )
}

/// Classify node status based on metrics
pub fn classify_status(latency_ms: Float, error_rate: Float) -> NodeStatus {
  case latency_ms, error_rate {
    l, e if l < 100.0 && e < 0.01 -> Healthy
    l, e if l < 500.0 && e < 0.05 -> Degraded
    _, _ -> Unreachable
  }
}

/// Compute cluster summary
pub fn summarize_cluster(nodes: List(NodeHealth)) -> ClusterHealth {
  let healthy = list.filter(nodes, fn(n) {
    case n.status {
      Healthy -> True
      _ -> False
    }
  })
  let total_latency = list.fold(nodes, 0.0, fn(acc, n) { acc +. n.latency_ms })
  let count = list.length(nodes)
  let avg = case count {
    0 -> 0.0
    c -> total_latency /. int.to_float(c)
  }
  ClusterHealth(
    nodes: nodes,
    healthy_count: list.length(healthy),
    total_count: count,
    avg_latency_ms: avg,
  )
}

/// Encode health report to JSON
pub fn encode_health(cluster: ClusterHealth) -> String {
  json.object([
    #("healthy_nodes", json.int(cluster.healthy_count)),
    #("total_nodes", json.int(cluster.total_count)),
    #("avg_latency_ms", json.float(cluster.avg_latency_ms)),
    #("nodes", json.array(cluster.nodes, fn(n) {
      json.object([
        #("node_id", json.string(n.node_id)),
        #("endpoint", json.string(n.endpoint)),
        #("latency_ms", json.float(n.latency_ms)),
        #("gpu_pct", json.float(n.gpu_utilization)),
        #("active", json.int(n.active_requests)),
      ])
    })),
  ])
  |> json.to_string()
}
