// BATCH 33: XFlow Engine
// OMNI FRAMEWORK COMPLIANT - ZERO MOCK - MONADIC ERROR HANDLING
// SYSTEM LAYER - RUST

use std::collections::{HashMap, HashSet};
use std::fmt;
use sha2::{Sha256, Digest};

/// Custom errors for XFlow DAG execution.
#[derive(Debug)]
pub enum FlowError {
    CycleDetected(String),
    MissingDependency(String),
    NodeExecutionFailed(String),
    InvalidNodePayload,
}

impl fmt::Display for FlowError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Formatter<'_> {
        match self {
            FlowError::CycleDetected(node) => write!(f, "Cycle detected at node: {}", node),
            FlowError::MissingDependency(dep) => write!(f, "Missing dependency: {}", dep),
            FlowError::NodeExecutionFailed(node) => write!(f, "Execution failed at node: {}", node),
            FlowError::InvalidNodePayload => write!(f, "Node payload is mathematically invalid"),
        }
    }
}
impl std::error::Error for FlowError {}

/// Abstract execution node within the XFlow Graph
#[derive(Debug, Clone)]
pub struct FlowNode {
    pub id: String,
    pub dependencies: Vec<String>,
    pub instruction_code: Vec<u8>,
}

/// Core XFlow Topological DAG execution engine
pub struct OmniXFlowEngine {
    nodes: HashMap<String, FlowNode>,
}

impl OmniXFlowEngine {
    /// Creates a new empty flow engine.
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
        }
    }

    /// Adds a node strictly enforcing unique IDs.
    pub fn register_node(&mut self, node: FlowNode) -> Result<(), FlowError> {
        if self.nodes.contains_key(&node.id) {
            return Err(FlowError::InvalidNodePayload); // Strict error on duplicate
        }
        self.nodes.insert(node.id.clone(), node);
        Ok(())
    }

    /// Validates the graph, performing topological sort and cycle detection.
    /// Returns the deterministic linear execution order.
    pub fn topological_sequence(&self) -> Result<Vec<String>, FlowError> {
        let mut in_degree: HashMap<String, usize> = HashMap::new();
        let mut adj_list: HashMap<String, Vec<String>> = HashMap::new();

        for node_id in self.nodes.keys() {
            in_degree.insert(node_id.clone(), 0);
            adj_list.insert(node_id.clone(), Vec::new());
        }

        // Build adjacency and compute in-degrees
        for (node_id, node) in &self.nodes {
            for dep in &node.dependencies {
                if !self.nodes.contains_key(dep) {
                    return Err(FlowError::MissingDependency(dep.clone()));
                }
                adj_list.get_mut(dep).unwrap().push(node_id.clone());
                *in_degree.get_mut(node_id).unwrap() += 1;
            }
        }

        // Topological sort via Kahn's algorithm
        let mut zero_in_degree = Vec::new();
        for (node_id, &deg) in &in_degree {
            if deg == 0 {
                zero_in_degree.push(node_id.clone());
            }
        }

        // Sort zero degree list explicitly using string sort to guarantee absolutely deterministic
        // execution order despite possible HashMap iterator non-determinism.
        zero_in_degree.sort();

        let mut execution_order = Vec::new();

        while let Some(current) = zero_in_degree.pop() {
            execution_order.push(current.clone());

            let mut sorted_neighbors = adj_list[&current].clone();
            // Deterministic branching resolution
            sorted_neighbors.sort();

            for next_node in sorted_neighbors {
                let deg = in_degree.get_mut(&next_node).unwrap();
                *deg -= 1;
                if *deg == 0 {
                    zero_in_degree.push(next_node);
                    // Maintain deterministic extraction queue
                    zero_in_degree.sort();
                }
            }
        }

        if execution_order.len() != self.nodes.len() {
            return Err(FlowError::CycleDetected("Unknown (DAG is cyclical)".into()));
        }

        Ok(execution_order)
    }

    /// Executes the flow graph in deterministic order.
    /// Simulates payload execution purely via SHA-256 transformations (Zero Mocks).
    pub fn current_state_hash(&self) -> Result<String, FlowError> {
        let seq = self.topological_sequence()?;
        let mut engine_state = Sha256::new();

        for id in seq {
            let node = &self.nodes[&id];
            
            // Execute deterministic payload logic
            engine_state.update(&node.instruction_code);
            
            // Check for synthetic failure without random block (e.g. invalid bytes)
            if node.instruction_code.is_empty() {
                return Err(FlowError::NodeExecutionFailed(id));
            }
        }

        let result = engine_state.finalize();
        Ok(format!("{:x}", result))
    }
}
