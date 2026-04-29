// Omni SubgraphRAG Graph Traversal (Rust)
// Ref: Graph-COM/SubgraphRAG — ICLR'25 | MIT
use std::collections::{HashMap, HashSet};
pub struct KGTriple { pub head: String, pub rel: String, pub tail: String }
pub fn extract_subgraph(adj: &HashMap<String, Vec<(String, String)>>, seeds: &[String], max_hops: usize) -> Vec<(String, String, String)> {
    let mut visited: HashSet<String> = seeds.iter().cloned().collect();
    let mut frontier: Vec<String> = seeds.to_vec();
    let mut triples = Vec::new();
    for _ in 0..max_hops {
        let mut next = Vec::new();
        for node in &frontier {
            if let Some(neighbors) = adj.get(node) {
                for (rel, neighbor) in neighbors {
                    triples.push((node.clone(), rel.clone(), neighbor.clone()));
                    if !visited.contains(neighbor) { visited.insert(neighbor.clone()); next.push(neighbor.clone()); }
                }
            }
        }
        frontier = next;
    }
    triples
}
