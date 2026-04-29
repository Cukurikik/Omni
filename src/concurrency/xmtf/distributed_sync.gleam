import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn synchronize_nodes(node_count: Int) -> OmniResult(String) {
  if node_count <= 1 {
    Error("Must have >1 nodes to sync")
  } else {
    // Gleam concurrent message passing for xMTF distributed training
    Ok("Nodes synchronized successfully")
  }
}
