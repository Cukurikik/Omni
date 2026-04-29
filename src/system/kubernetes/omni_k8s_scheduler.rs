// OMNI K8s Scheduler Engine — System Layer (Rust)
// Absorbing kubernetes/kubernetes
// Deterministic Pod node placement affinity evaluation

use std::collections::HashMap;

#[derive(Debug)]
pub enum K8sError {
    EmptyTopology,
}

type Result<T> = std::result::Result<T, K8sError>;

#[derive(Clone)]
pub struct NodeSpec {
    pub id: String,
    pub available_cpu: u32,
    pub available_mem_mb: u32,
    pub labels: HashMap<String, String>,
}

pub struct PodSpec {
    pub req_cpu: u32,
    pub req_mem_mb: u32,
    pub node_selector: HashMap<String, String>,
}

pub struct OmniK8sScheduler {
    scheduling_cycles: u64,
}

impl OmniK8sScheduler {
    pub fn new() -> Self {
        Self { scheduling_cycles: 0 }
    }

    /// Evaluates exact filter and score mechanics for node placement topology bounds
    pub fn execute_scheduler_cycle(
        &mut self,
        pod: &PodSpec,
        nodes: &[NodeSpec]
    ) -> Result<Option<String>> {
        if nodes.is_empty() {
            return Err(K8sError::EmptyTopology);
        }

        self.scheduling_cycles += 1;

        let mut best_node: Option<String> = None;
        let mut best_score = -1;

        for node in nodes {
            // Stage 1: Predicate Filters bounds (Resources + Node Selector)
            if node.available_cpu < pod.req_cpu || node.available_mem_mb < pod.req_mem_mb {
                continue;
            }

            let mut selector_match = true;
            for (k, v) in &pod.node_selector {
                if let Some(node_val) = node.labels.get(k) {
                    if node_val != v {
                        selector_match = false;
                        break;
                    }
                } else {
                    selector_match = false;
                    break;
                }
            }

            if !selector_match {
                continue; // Predicate failed
            }

            // Stage 2: Priority Scoring Evaluator (LeastRequestedPriority implementation mapping)
            let cpu_score = ((node.available_cpu - pod.req_cpu) as f32 / node.available_cpu as f32) * 100.0;
            let mem_score = ((node.available_mem_mb - pod.req_mem_mb) as f32 / node.available_mem_mb as f32) * 100.0;
            
            let final_score = ((cpu_score + mem_score) / 2.0) as i32;

            if final_score > best_score {
                best_score = final_score;
                best_node = Some(node.id.clone());
            }
        }

        Ok(best_node)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniK8sScheduler".to_string());
        map.insert("cycles".to_string(), self.scheduling_cycles.to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
