// moe_fault_detector.rs — Distributed Fault Detector for MoE
// Layer: System / Health — MoE Cluster Resiliency
//
// Rust-based fault detector agent for distributed MoE training.
// Uses gossip protocol and heartbeat monitoring to detect node failures,
// GPU hangs, or network partitions, triggering automatic expert reallocation.

use std::collections::{HashMap, HashSet};
use std::sync::{Arc, RwLock};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NodeStatus {
    Healthy,
    Suspected,
    Dead,
}

#[derive(Debug, Clone)]
pub struct NodeInfo {
    pub node_id: u32,
    pub address: String,
    pub status: NodeStatus,
    pub last_heartbeat: Instant,
    pub hosted_experts: Vec<u16>,
    pub load_metric: f32,
}

pub struct MoEFaultDetector {
    local_node_id: u32,
    nodes: RwLock<HashMap<u32, NodeInfo>>,
    suspect_timeout: Duration,
    dead_timeout: Duration,
}

impl MoEFaultDetector {
    pub fn new(local_node_id: u32) -> Self {
        Self {
            local_node_id,
            nodes: RwLock::new(HashMap::new()),
            suspect_timeout: Duration::from_secs(5),
            dead_timeout: Duration::from_secs(15),
        }
    }

    /// Register a node in the cluster.
    pub fn register_node(&self, node_id: u32, address: String, experts: Vec<u16>) {
        let info = NodeInfo {
            node_id,
            address,
            status: NodeStatus::Healthy,
            last_heartbeat: Instant::now(),
            hosted_experts: experts,
            load_metric: 0.0,
        };
        self.nodes.write().unwrap().insert(node_id, info);
    }

    /// Update heartbeat received from a node.
    pub fn process_heartbeat(&self, node_id: u32, load: f32) {
        if let Some(node) = self.nodes.write().unwrap().get_mut(&node_id) {
            node.last_heartbeat = Instant::now();
            node.load_metric = load;
            
            // If it was suspected or dead, mark as healthy again
            if node.status != NodeStatus::Healthy {
                node.status = NodeStatus::Healthy;
            }
        }
    }

    /// Periodic sweep to check for timeouts. Returns a list of newly dead nodes.
    pub fn check_timeouts(&self) -> Vec<u32> {
        let mut newly_dead = Vec::new();
        let now = Instant::now();
        let mut nodes = self.nodes.write().unwrap();

        for (id, node) in nodes.iter_mut() {
            if *id == self.local_node_id { continue; }

            let elapsed = now.duration_since(node.last_heartbeat);

            if elapsed > self.dead_timeout && node.status != NodeStatus::Dead {
                node.status = NodeStatus::Dead;
                newly_dead.push(*id);
            } else if elapsed > self.suspect_timeout && node.status == NodeStatus::Healthy {
                node.status = NodeStatus::Suspected;
            }
        }

        newly_dead
    }

    /// Get all experts hosted on dead nodes (needs reallocation).
    pub fn get_orphaned_experts(&self) -> HashSet<u16> {
        let nodes = self.nodes.read().unwrap();
        let mut orphaned = HashSet::new();

        for node in nodes.values() {
            if node.status == NodeStatus::Dead {
                for &exp in &node.hosted_experts {
                    orphaned.insert(exp);
                }
            }
        }
        orphaned
    }

    /// Reallocate orphaned experts to healthy nodes based on load.
    pub fn calculate_reallocation(&self) -> HashMap<u16, u32> {
        let orphaned = self.get_orphaned_experts();
        if orphaned.is_empty() {
            return HashMap::new();
        }

        let nodes = self.nodes.read().unwrap();
        let mut healthy_nodes: Vec<_> = nodes.values()
            .filter(|n| n.status == NodeStatus::Healthy)
            .collect();

        // Sort by load (ascending)
        healthy_nodes.sort_by(|a, b| a.load_metric.partial_cmp(&b.load_metric).unwrap());

        let mut reallocation = HashMap::new();
        let mut node_idx = 0;

        // Round-robin allocation to healthy nodes
        for expert_id in orphaned {
            if healthy_nodes.is_empty() {
                break; // Cluster completely down
            }
            let target_node = healthy_nodes[node_idx].node_id;
            reallocation.insert(expert_id, target_node);
            node_idx = (node_idx + 1) % healthy_nodes.len();
        }

        reallocation
    }
}
