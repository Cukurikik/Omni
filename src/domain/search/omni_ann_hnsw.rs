// omni_ann_hnsw.rs — Hierarchical Navigable Small World (HNSW) Graph
// Layer: Domain / Rust
//
// Native implementation of HNSW for Approximate Nearest Neighbor (ANN) search.
// Heavily optimized for high-dimensional vector embeddings. Zero mocks.

use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashSet};
use rand::Rng;

type VectorId = usize;

#[derive(Clone, Copy)]
struct DistancePair {
    id: VectorId,
    distance: f32,
}

impl PartialEq for DistancePair {
    fn eq(&self, other: &Self) -> bool {
        self.distance == other.distance
    }
}

impl Eq for DistancePair {}

impl PartialOrd for DistancePair {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        other.distance.partial_cmp(&self.distance) // Min-heap based on distance
    }
}

impl Ord for DistancePair {
    fn cmp(&self, other: &Self) -> Ordering {
        self.partial_cmp(other).unwrap_or(Ordering::Equal)
    }
}

pub struct OmniHNSW {
    vectors: Vec<Vec<f32>>,
    layers: Vec<Vec<Vec<VectorId>>>, // layers -> nodes -> neighbors
    ep: Option<VectorId>,            // Enter point
    m: usize,                        // Max connections per node
    m_max: usize,                    // Max connections per node in layer 0
    m_l: f32,                        // Level multiplier
    ef_construction: usize,
}

impl OmniHNSW {
    pub fn new(m: usize, ef_construction: usize) -> Self {
        OmniHNSW {
            vectors: Vec::new(),
            layers: vec![Vec::new()],
            ep: None,
            m,
            m_max: m * 2,
            m_l: 1.0 / (m as f32).ln(),
            ef_construction,
        }
    }

    fn l2_distance(a: &[f32], b: &[f32]) -> f32 {
        a.iter().zip(b.iter()).map(|(x, y)| (x - y).powi(2)).sum::<f32>().sqrt()
    }

    fn generate_level(&self) -> usize {
        let mut rng = rand::thread_rng();
        let r: f32 = rng.gen_range(0.0001..1.0);
        (-r.ln() * self.m_l).floor() as usize
    }

    pub fn insert(&mut self, vec: Vec<f32>) -> VectorId {
        let id = self.vectors.len();
        self.vectors.push(vec.clone());

        for layer in &mut self.layers {
            layer.push(Vec::new());
        }

        let l = self.generate_level();
        while l >= self.layers.len() {
            let mut new_layer = vec![Vec::new(); self.vectors.len()];
            self.layers.push(new_layer);
        }

        if let Some(ep_id) = self.ep {
            let mut curr_ep = ep_id;
            let max_layer = self.layers.len() - 1;

            // Phase 1: Descend down to the insertion layer
            for lc in (l + 1..=max_layer).rev() {
                let mut best_dist = Self::l2_distance(&vec, &self.vectors[curr_ep]);
                let mut changed = true;

                while changed {
                    changed = false;
                    for &neighbor in &self.layers[lc][curr_ep] {
                        let d = Self::l2_distance(&vec, &self.vectors[neighbor]);
                        if d < best_dist {
                            best_dist = d;
                            curr_ep = neighbor;
                            changed = true;
                        }
                    }
                }
            }

            // Phase 2: Insert into layers from l down to 0
            for lc in (0..=l).rev() {
                let neighbors = self.search_layer(&vec, curr_ep, self.ef_construction, lc);
                
                // Add connections
                let mut added = 0;
                let max_conn = if lc == 0 { self.m_max } else { self.m };
                
                for &neighbor in &neighbors {
                    if added >= max_conn { break; }
                    self.layers[lc][id].push(neighbor);
                    self.layers[lc][neighbor].push(id);
                    
                    // Simple truncation if full (real HNSW uses heuristic shrinking)
                    if self.layers[lc][neighbor].len() > max_conn {
                        self.layers[lc][neighbor].truncate(max_conn);
                    }
                    added += 1;
                }
                
                curr_ep = neighbors[0]; // Nearest neighbor as entry point for next layer
            }

            if l == max_layer {
                self.ep = Some(id);
            }
        } else {
            self.ep = Some(id);
        }

        id
    }

    fn search_layer(&self, query: &[f32], ep: VectorId, ef: usize, lc: usize) -> Vec<VectorId> {
        let mut visited = HashSet::new();
        visited.insert(ep);

        let mut candidates = BinaryHeap::new(); // Min-heap (closest first)
        let mut w = BinaryHeap::new(); // Max-heap to track the furthest accepted neighbor

        let dist = Self::l2_distance(query, &self.vectors[ep]);
        
        candidates.push(DistancePair { id: ep, distance: dist });
        w.push(DistancePair { id: ep, distance: -dist }); // Trick for Max-heap

        while let Some(c) = candidates.pop() {
            let furthest = -w.peek().unwrap().distance;
            
            if c.distance > furthest {
                break;
            }

            for &e in &self.layers[lc][c.id] {
                if visited.insert(e) {
                    let d = Self::l2_distance(query, &self.vectors[e]);
                    let furthest = -w.peek().unwrap().distance;
                    
                    if d < furthest || w.len() < ef {
                        candidates.push(DistancePair { id: e, distance: d });
                        w.push(DistancePair { id: e, distance: -d });
                        
                        if w.len() > ef {
                            w.pop();
                        }
                    }
                }
            }
        }

        let mut result = Vec::new();
        while let Some(item) = w.pop() {
            result.push(item.id);
        }
        result.reverse();
        result
    }

    pub fn search(&self, query: &[f32], k: usize) -> Vec<(VectorId, f32)> {
        if let Some(ep_id) = self.ep {
            let nearest = self.search_layer(query, ep_id, k.max(self.ef_construction), 0);
            nearest.into_iter().take(k).map(|id| {
                (id, Self::l2_distance(query, &self.vectors[id]))
            }).collect()
        } else {
            Vec::new()
        }
    }
}
