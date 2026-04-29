/// OMNI MILVUS: HNSW (Hierarchical Navigable Small World) Index Math
/// Rust implementation of the greedy routing algorithm on a proximity graph.
/// Source: milvus-io/milvus

use std::cmp::Ordering;
use std::collections::BinaryHeap;

#[derive(Debug)]
pub enum HNSWError {
    VectorDimensionMismatch,
    NodeNotFound,
}

// Vector wrapper for Euclidean distance calculation
pub struct Vector(pub Vec<f32>);

impl Vector {
    pub fn distance_to(&self, other: &Vector) -> Result<f32, HNSWError> {
        if self.0.len() != other.0.len() {
            return Err(HNSWError::VectorDimensionMismatch);
        }
        let dist_sq: f32 = self.0.iter().zip(other.0.iter())
            .map(|(a, b)| (a - b) * (a - b))
            .sum();
        Ok(dist_sq.sqrt())
    }
}

// Represents a node in the graph
pub struct HNSWNode {
    pub id: usize,
    pub vector: Vector,
    pub neighbors: Vec<usize>, // IDs of adjacent nodes
}

// Priority queue wrapper for searching
#[derive(PartialEq)]
struct OrderedNode {
    id: usize,
    distance: f32,
}

impl Eq for OrderedNode {}

impl PartialOrd for OrderedNode {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // Reverse ordering so BinaryHeap acts as a Min-Heap
        other.distance.partial_cmp(&self.distance)
    }
}

impl Ord for OrderedNode {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap_or(Ordering::Equal)
    }
}

pub struct HNSWGraph {
    pub nodes: Vec<HNSWNode>,
}

impl HNSWGraph {
    /// Greedy search algorithm for navigating the graph towards a query vector.
    pub fn greedy_search(&self, start_node_id: usize, query: &Vector, ef: usize) -> Result<Vec<usize>, HNSWError> {
        if start_node_id >= self.nodes.len() {
            return Err(HNSWError::NodeNotFound);
        }

        let mut candidates = BinaryHeap::new();
        let mut visited = vec![false; self.nodes.len()];
        let mut top_results = Vec::new(); // Store best elements found so far

        let start_node = &self.nodes[start_node_id];
        let initial_dist = start_node.vector.distance_to(query)?;

        candidates.push(OrderedNode { id: start_node_id, distance: initial_dist });
        visited[start_node_id] = true;

        while let Some(current) = candidates.pop() {
            // Add to results
            top_results.push(current.id);
            if top_results.len() >= ef {
                break;
            }

            let node = &self.nodes[current.id];

            for &neighbor_id in &node.neighbors {
                if !visited[neighbor_id] {
                    visited[neighbor_id] = true;
                    let neighbor_dist = self.nodes[neighbor_id].vector.distance_to(query)?;
                    
                    // If the neighbor is closer than the current node, we explore it
                    if neighbor_dist < current.distance {
                         candidates.push(OrderedNode { id: neighbor_id, distance: neighbor_dist });
                    }
                }
            }
        }

        Ok(top_results)
    }
}
