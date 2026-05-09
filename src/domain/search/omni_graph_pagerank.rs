// omni_graph_pagerank.rs — PageRank Algorithm
// Layer: Domain / Search
//
// Computes the PageRank scores for a directed graph, determining the relative
// importance of nodes based on incoming edge structure. Essential for Search
// Engine algorithms and social network influencer detection. Zero mock.

use std::collections::HashMap;

pub struct OmniGraph {
    // Map Node -> List of Outgoing Nodes
    pub adjacency_list: HashMap<String, Vec<String>>,
}

impl OmniGraph {
    pub fn new() -> Self {
        OmniGraph {
            adjacency_list: HashMap::new(),
        }
    }

    pub fn add_edge(&mut self, from: String, to: String) {
        self.adjacency_list.entry(from.clone()).or_insert_with(Vec::new).push(to);
        // Ensure the 'to' node exists in the graph even if it has no outgoing edges
        self.adjacency_list.entry(from).or_insert_with(Vec::new);
    }

    /// Computes PageRank for all nodes
    /// `damping_factor`: usually 0.85
    /// `max_iterations`: convergence limit
    pub fn compute_pagerank(&self, damping_factor: f64, max_iterations: usize) -> HashMap<String, f64> {
        let n = self.adjacency_list.len();
        if n == 0 {
            return HashMap::new();
        }

        let initial_rank = 1.0 / (n as f64);
        let mut ranks: HashMap<String, f64> = self.adjacency_list.keys()
            .map(|k| (k.clone(), initial_rank))
            .collect();

        // Calculate incoming edges for each node
        // Map Node -> List of (Incoming Node, Out-degree of Incoming Node)
        let mut incoming_edges: HashMap<String, Vec<(String, usize)>> = HashMap::new();
        for (node, _) in &self.adjacency_list {
            incoming_edges.insert(node.clone(), Vec::new());
        }

        for (from, to_nodes) in &self.adjacency_list {
            let out_degree = to_nodes.len();
            for to in to_nodes {
                incoming_edges.get_mut(to).unwrap().push((from.clone(), out_degree));
            }
        }

        // Iterative PageRank computation
        for _ in 0..max_iterations {
            let mut new_ranks = HashMap::new();
            let random_jump_prob = (1.0 - damping_factor) / (n as f64);

            for node in self.adjacency_list.keys() {
                let mut rank_sum = 0.0;
                
                // Sum ranks of incoming nodes divided by their out-degree
                for (in_node, out_degree) in incoming_edges.get(node).unwrap() {
                    let in_rank = ranks.get(in_node).unwrap();
                    rank_sum += in_rank / (*out_degree as f64);
                }

                let new_rank = random_jump_prob + (damping_factor * rank_sum);
                new_ranks.insert(node.clone(), new_rank);
            }

            // Normalization (handling sink nodes implicitly through sum)
            let sum: f64 = new_ranks.values().sum();
            for (node, rank) in new_ranks.iter_mut() {
                *rank += (1.0 - sum) / (n as f64);
            }

            ranks = new_ranks;
        }

        ranks
    }
}
