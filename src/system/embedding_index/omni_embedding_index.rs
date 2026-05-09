/// omni_embedding_index.rs — Vector Embedding Index Engine
/// Inspired by: FashionCLIP + Marqo vector search
/// Layer: System / Rust
///
/// HNSW (Hierarchical Navigable Small World) index for high-dimensional
/// embedding similarity search. Optimized for fashion/image retrieval.

use std::collections::{BinaryHeap, HashMap, HashSet};
use std::cmp::Ordering;

#[derive(Clone, Debug)]
pub struct EmbeddingVector {
    pub id: u64,
    pub data: Vec<f32>,
    pub metadata: HashMap<String, String>,
}

#[derive(Clone, Debug)]
struct SearchResult {
    id: u64,
    distance: f32,
}

impl PartialEq for SearchResult {
    fn eq(&self, other: &Self) -> bool {
        self.distance == other.distance
    }
}

impl Eq for SearchResult {}

impl PartialOrd for SearchResult {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        // Min-heap: reverse ordering
        other.distance.partial_cmp(&self.distance)
    }
}

impl Ord for SearchResult {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap_or(Ordering::Equal)
    }
}

#[derive(Clone, Debug)]
pub struct HNSWConfig {
    pub m: usize,               // max connections per node
    pub m_max0: usize,          // max connections at layer 0
    pub ef_construction: usize, // beam width during construction
    pub ef_search: usize,       // beam width during search
    pub max_level: usize,
    pub dim: usize,
}

impl Default for HNSWConfig {
    fn default() -> Self {
        Self {
            m: 16,
            m_max0: 32,
            ef_construction: 200,
            ef_search: 50,
            max_level: 6,
            dim: 512,
        }
    }
}

struct HNSWNode {
    id: u64,
    vector: Vec<f32>,
    connections: Vec<Vec<u64>>,  // connections per level
    level: usize,
    metadata: HashMap<String, String>,
}

/// Distance metric
pub enum DistanceMetric {
    Cosine,
    Euclidean,
    DotProduct,
}

fn cosine_distance(a: &[f32], b: &[f32]) -> f32 {
    let mut dot = 0.0f32;
    let mut norm_a = 0.0f32;
    let mut norm_b = 0.0f32;
    for i in 0..a.len() {
        dot += a[i] * b[i];
        norm_a += a[i] * a[i];
        norm_b += b[i] * b[i];
    }
    let denom = (norm_a.sqrt() * norm_b.sqrt()).max(1e-10);
    1.0 - dot / denom
}

fn euclidean_distance(a: &[f32], b: &[f32]) -> f32 {
    let mut sum = 0.0f32;
    for i in 0..a.len() {
        let d = a[i] - b[i];
        sum += d * d;
    }
    sum.sqrt()
}

fn dot_product_distance(a: &[f32], b: &[f32]) -> f32 {
    let mut dot = 0.0f32;
    for i in 0..a.len() {
        dot += a[i] * b[i];
    }
    -dot // Negate so lower is better
}

pub struct OmniEmbeddingIndex {
    config: HNSWConfig,
    nodes: HashMap<u64, HNSWNode>,
    entry_point: Option<u64>,
    max_level: usize,
    metric: DistanceMetric,
    rng_seed: u64,
}

impl OmniEmbeddingIndex {
    pub fn new(config: HNSWConfig, metric: DistanceMetric) -> Self {
        Self {
            config,
            nodes: HashMap::new(),
            entry_point: None,
            max_level: 0,
            metric,
            rng_seed: 42,
        }
    }

    fn distance(&self, a: &[f32], b: &[f32]) -> f32 {
        match self.metric {
            DistanceMetric::Cosine => cosine_distance(a, b),
            DistanceMetric::Euclidean => euclidean_distance(a, b),
            DistanceMetric::DotProduct => dot_product_distance(a, b),
        }
    }

    fn random_level(&mut self) -> usize {
        // Simple LCG for deterministic level assignment
        self.rng_seed = self.rng_seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        let r = (self.rng_seed >> 33) as f64 / (1u64 << 31) as f64;
        let ml = 1.0 / (self.config.m as f64).ln();
        let level = (-r.ln() * ml) as usize;
        level.min(self.config.max_level)
    }

    pub fn insert(&mut self, embedding: EmbeddingVector) {
        assert_eq!(embedding.data.len(), self.config.dim, "Dimension mismatch");
        let id = embedding.id;
        let level = self.random_level();

        let node = HNSWNode {
            id,
            vector: embedding.data,
            connections: (0..=level).map(|_| Vec::new()).collect(),
            level,
            metadata: embedding.metadata,
        };

        if self.nodes.is_empty() {
            self.entry_point = Some(id);
            self.max_level = level;
            self.nodes.insert(id, node);
            return;
        }

        let entry = self.entry_point.unwrap();
        self.nodes.insert(id, node);

        // Connect node using greedy search at each level
        let mut current = entry;
        for lev in (0..=self.max_level).rev() {
            if lev > level {
                // Just greedy-search to find closest at this level
                let closest = self.search_layer_greedy(current, id, lev);
                current = closest;
            } else {
                // Search and connect at this level
                let neighbors = self.search_layer(current, id, self.config.ef_construction, lev);
                let max_conn = if lev == 0 { self.config.m_max0 } else { self.config.m };
                let selected: Vec<u64> = neighbors.into_iter()
                    .take(max_conn)
                    .map(|r| r.id)
                    .collect();

                // Add bidirectional connections
                if let Some(node) = self.nodes.get_mut(&id) {
                    if lev < node.connections.len() {
                        node.connections[lev] = selected.clone();
                    }
                }

                for &neighbor_id in &selected {
                    if let Some(neighbor) = self.nodes.get_mut(&neighbor_id) {
                        if lev < neighbor.connections.len() {
                            neighbor.connections[lev].push(id);
                            if neighbor.connections[lev].len() > max_conn {
                                // Prune to keep only closest
                                let nv = neighbor.vector.clone();
                                let nodes_ref = &self.nodes;
                                neighbor.connections[lev].sort_by(|a, b| {
                                    let da = if let Some(na) = nodes_ref.get(a) {
                                        cosine_distance(&nv, &na.vector)
                                    } else { f32::MAX };
                                    let db = if let Some(nb) = nodes_ref.get(b) {
                                        cosine_distance(&nv, &nb.vector)
                                    } else { f32::MAX };
                                    da.partial_cmp(&db).unwrap_or(Ordering::Equal)
                                });
                                neighbor.connections[lev].truncate(max_conn);
                            }
                        }
                    }
                }

                if !selected.is_empty() {
                    current = selected[0];
                }
            }
        }

        if level > self.max_level {
            self.max_level = level;
            self.entry_point = Some(id);
        }
    }

    fn search_layer_greedy(&self, start: u64, target: u64, level: usize) -> u64 {
        let target_vec = &self.nodes[&target].vector;
        let mut current = start;
        let mut current_dist = self.distance(target_vec, &self.nodes[&current].vector);

        loop {
            let mut improved = false;
            if let Some(node) = self.nodes.get(&current) {
                if level < node.connections.len() {
                    for &neighbor in &node.connections[level] {
                        if let Some(n) = self.nodes.get(&neighbor) {
                            let d = self.distance(target_vec, &n.vector);
                            if d < current_dist {
                                current_dist = d;
                                current = neighbor;
                                improved = true;
                            }
                        }
                    }
                }
            }
            if !improved {
                break;
            }
        }
        current
    }

    fn search_layer(&self, start: u64, target: u64, ef: usize, level: usize) -> Vec<SearchResult> {
        let target_vec = &self.nodes[&target].vector;
        let mut visited = HashSet::new();
        let mut candidates = BinaryHeap::new();
        let mut results = BinaryHeap::new();

        let start_dist = self.distance(target_vec, &self.nodes[&start].vector);
        candidates.push(SearchResult { id: start, distance: start_dist });
        results.push(SearchResult { id: start, distance: -start_dist }); // Max-heap for worst
        visited.insert(start);

        while let Some(SearchResult { id: current, distance: _ }) = candidates.pop() {
            if let Some(node) = self.nodes.get(&current) {
                if level < node.connections.len() {
                    for &neighbor in &node.connections[level] {
                        if visited.insert(neighbor) {
                            if let Some(n) = self.nodes.get(&neighbor) {
                                let d = self.distance(target_vec, &n.vector);
                                candidates.push(SearchResult { id: neighbor, distance: d });
                                results.push(SearchResult { id: neighbor, distance: -d });
                                if results.len() > ef {
                                    results.pop();
                                }
                            }
                        }
                    }
                }
            }
        }

        results.into_sorted_vec().into_iter()
            .map(|r| SearchResult { id: r.id, distance: -r.distance })
            .collect()
    }

    /// Search for the k nearest neighbors to a query vector
    pub fn search(&self, query: &[f32], k: usize) -> Vec<(u64, f32)> {
        assert_eq!(query.len(), self.config.dim);
        if self.nodes.is_empty() {
            return vec![];
        }

        let entry = self.entry_point.unwrap();
        let mut current = entry;

        // Traverse from top level to level 1
        for lev in (1..=self.max_level).rev() {
            loop {
                let mut improved = false;
                if let Some(node) = self.nodes.get(&current) {
                    if lev < node.connections.len() {
                        for &neighbor in &node.connections[lev] {
                            if let Some(n) = self.nodes.get(&neighbor) {
                                let d_neighbor = self.distance(query, &n.vector);
                                let d_current = self.distance(query, &self.nodes[&current].vector);
                                if d_neighbor < d_current {
                                    current = neighbor;
                                    improved = true;
                                }
                            }
                        }
                    }
                }
                if !improved { break; }
            }
        }

        // Search at level 0 with beam
        let mut visited = HashSet::new();
        let mut candidates = BinaryHeap::new();
        let mut results: Vec<(u64, f32)> = Vec::new();

        let d = self.distance(query, &self.nodes[&current].vector);
        candidates.push(SearchResult { id: current, distance: d });
        visited.insert(current);

        while let Some(SearchResult { id, distance }) = candidates.pop() {
            results.push((id, distance));
            if let Some(node) = self.nodes.get(&id) {
                if !node.connections.is_empty() {
                    for &neighbor in &node.connections[0] {
                        if visited.insert(neighbor) {
                            if let Some(n) = self.nodes.get(&neighbor) {
                                let nd = self.distance(query, &n.vector);
                                candidates.push(SearchResult { id: neighbor, distance: nd });
                            }
                        }
                    }
                }
            }
        }

        results.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(Ordering::Equal));
        results.truncate(k);
        results
    }

    pub fn len(&self) -> usize {
        self.nodes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.nodes.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_insert_and_search() {
        let config = HNSWConfig { dim: 4, ..Default::default() };
        let mut index = OmniEmbeddingIndex::new(config, DistanceMetric::Cosine);

        for i in 0..10u64 {
            index.insert(EmbeddingVector {
                id: i,
                data: vec![i as f32, 0.0, 0.0, 1.0],
                metadata: HashMap::new(),
            });
        }

        assert_eq!(index.len(), 10);

        let results = index.search(&[5.0, 0.0, 0.0, 1.0], 3);
        assert!(!results.is_empty());
        assert_eq!(results[0].0, 5); // exact match should be first
    }
}
