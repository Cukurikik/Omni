// OMNI HDFS Block Map Engine — System Layer (Rust)
// Absorbing apache/hadoop distributed file bounds
// Block topology replication distance mapping

use std::collections::HashMap;

#[derive(Debug)]
pub enum HadoopError {
    InvalidReplication,
}

type Result<T> = std::result::Result<T, HadoopError>;

pub struct OmniHdfsBlockMap {
    blocks_allocated: u64,
}

impl OmniHdfsBlockMap {
    pub fn new() -> Self {
        Self { blocks_allocated: 0 }
    }

    /// Evaluates exact replica placement geography mappings.
    /// Rack awareness zero-mock layout rules for HDFS constraint topologies.
    pub fn allocate_block_replicas(
        &mut self,
        block_id: &str,
        datanodes: &[(String, String)], // (NodeID, RackID)
        replication_factor: usize
    ) -> Result<Vec<String>> {
        if replication_factor == 0 || replication_factor > datanodes.len() {
            return Err(HadoopError::InvalidReplication);
        }

        self.blocks_allocated += 1;

        let mut selected_nodes = Vec::new();
        let mut selected_racks = HashMap::new();

        // 1st Replica: Random/Local node (using first available for deterministic math)
        let first_node = &datanodes[0];
        selected_nodes.push(first_node.0.clone());
        *selected_racks.entry(first_node.1.clone()).or_insert(0) += 1;

        // 2nd Replica: Different Rack (Exact structural requirement)
        let mut second_index = Option::None;
        for (i, node) in datanodes.iter().enumerate().skip(1) {
            if !selected_racks.contains_key(&node.1) {
                selected_nodes.push(node.0.clone());
                *selected_racks.entry(node.1.clone()).or_insert(0) += 1;
                second_index = Some(i);
                break;
            }
        }

        if selected_nodes.len() < 2 && replication_factor >= 2 {
            // Fallback if network topology is entirely single-rack
            selected_nodes.push(datanodes[1].0.clone());
            *selected_racks.entry(datanodes[1].1.clone()).or_insert(0) += 1;
        }

        // 3rd Replica: Same rack as 2nd, different Node
        if replication_factor >= 3 {
             let mut third_selected = false;
             if let Some(idx) = second_index {
                 let second_rack = &datanodes[idx].1;
                 for node in datanodes.iter().skip(idx + 1) {
                     if &node.1 == second_rack {
                         selected_nodes.push(node.0.clone());
                         *selected_racks.entry(node.1.clone()).or_insert(0) += 1;
                         third_selected = true;
                         break;
                     }
                 }
             }

             if !third_selected {
                  for node in datanodes.iter() {
                      if !selected_nodes.contains(&node.0) {
                          selected_nodes.push(node.0.clone());
                          break;
                      }
                  }
             }
        }

        // Remaining replicas: Arbitrary unique nodes
        for node in datanodes.iter() {
            if selected_nodes.len() >= replication_factor {
                break;
            }
            if !selected_nodes.contains(&node.0) {
                selected_nodes.push(node.0.clone());
            }
        }

        Ok(selected_nodes)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniHdfsBlockMap".to_string());
        map.insert("blocks".to_string(), self.blocks_allocated.to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
