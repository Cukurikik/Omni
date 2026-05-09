import gleam/erlang/process.{type Subject}
import gleam/otp/actor

// Omni Distributed Synchronizer (Gleam)
// Concurrency Layer
// Type-safe actor implementation running on the BEAM virtual machine.
// Synchronizes cluster state globally for Transformer pipeline deployments.

pub type Message {
  UpdateClusterState(node_id: String, vram_usage: Int)
  GetGlobalState(reply_to: Subject(ClusterState))
}

pub type ClusterState {
  ClusterState(nodes: List(NodeStatus))
}

pub type NodeStatus {
  NodeStatus(node_id: String, vram_usage: Int)
}

pub fn start_link() -> Result(Subject(Message), actor.StartError) {
  actor.start(ClusterState(nodes: []), handle_message)
}

fn handle_message(message: Message, state: ClusterState) -> actor.Next(Message, ClusterState) {
  case message {
    UpdateClusterState(node_id, vram_usage) -> {
      let new_node = NodeStatus(node_id, vram_usage)
      // Filter out old status and prepend new status
      let updated_nodes = [new_node, ..list_remove_node(state.nodes, node_id)]
      actor.continue(ClusterState(nodes: updated_nodes))
    }

    GetGlobalState(client) -> {
      process.send(client, state)
      actor.continue(state)
    }
  }
}

fn list_remove_node(nodes: List(NodeStatus), target_id: String) -> List(NodeStatus) {
  case nodes {
    [] -> []
    [NodeStatus(id, vram), ..rest] if id == target_id -> rest
    [other, ..rest] -> [other, ..list_remove_node(rest, target_id)]
  }
}
