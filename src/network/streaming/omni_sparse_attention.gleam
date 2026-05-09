// OMNI Concurrency Layer: Type-safe concurrent sparse attention patterns
// Implemented in Gleam for the Erlang BEAM VM ecosystem.

import gleam/list
import gleam/result

pub type AttentionNode {
  AttentionNode(
    id: Int,
    query_vector: List(Float),
    key_vector: List(Float),
    value_vector: List(Float),
  )
}

pub type SparseConnection {
  SparseConnection(source_id: Int, target_id: Int)
}

pub type AttentionError {
  DimensionMismatch
  TargetNotFound
}

/// Computes the dot product of two vectors safely.
fn dot_product(v1: List(Float), v2: List(Float)) -> Result(Float, AttentionError) {
  case list.length(v1) == list.length(v2) {
    True -> {
      let pairs = list.zip(v1, v2)
      let sum = list.fold(pairs, 0.0, fn(acc, pair) { acc +. pair.0 *. pair.1 })
      Ok(sum)
    }
    False -> Error(DimensionMismatch)
  }
}

/// Evaluates a sparse attention graph safely over the BEAM cluster
pub fn evaluate_sparse_connections(
  nodes: List(AttentionNode),
  connections: List(SparseConnection),
) -> Result(List(Float), AttentionError) {
  // In a real BEAM application, these would be mapped out to Actor processes via OTP.
  // Here we functionally fold over the connections ensuring type safety.
  
  let scores_result = list.try_map(connections, fn(conn) {
    let source_opt = list.find(nodes, fn(n) { n.id == conn.source_id })
    let target_opt = list.find(nodes, fn(n) { n.id == conn.target_id })
    
    case source_opt, target_opt {
      Ok(source), Ok(target) -> {
        dot_product(source.query_vector, target.key_vector)
      }
      _, _ -> Error(TargetNotFound)
    }
  })
  
  scores_result
}
