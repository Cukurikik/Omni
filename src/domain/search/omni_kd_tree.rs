// omni_kd_tree.rs — KD-Tree Spatial Indexing
// Layer: Domain / Rust
//
// Implements a k-dimensional tree for extremely fast spatial queries
// (Nearest Neighbor search). Used in geospatial clustering and basic 
// vector DB routing. Zero mock.

use std::cmp::Ordering;

#[derive(Debug, Clone)]
pub struct KDNode {
    pub point: Vec<f64>,
    pub id: usize,
    pub left: Option<Box<KDNode>>,
    pub right: Option<Box<KDNode>>,
}

pub struct OmniKDTree {
    pub root: Option<Box<KDNode>>,
    pub k: usize,
}

impl OmniKDTree {
    pub fn new(k: usize) -> Self {
        OmniKDTree { root: None, k }
    }

    /// Builds the KD-Tree recursively. Consumes the input points.
    pub fn build(&mut self, mut points: Vec<(Vec<f64>, usize)>) {
        if points.is_empty() {
            self.root = None;
            return;
        }
        self.root = Some(Box::new(Self::build_recursive(&mut points, 0, self.k)));
    }

    fn build_recursive(points: &mut [(Vec<f64>, usize)], depth: usize, k: usize) -> KDNode {
        let axis = depth % k;
        
        // Sort points by the current axis
        points.sort_by(|a, b| {
            a.0[axis].partial_cmp(&b.0[axis]).unwrap_or(Ordering::Equal)
        });

        let median_idx = points.len() / 2;
        let (left, right) = points.split_at_mut(median_idx);
        let (median, right_remainder) = right.split_first_mut().unwrap();

        let left_node = if left.is_empty() {
            None
        } else {
            Some(Box::new(Self::build_recursive(left, depth + 1, k)))
        };

        let right_node = if right_remainder.is_empty() {
            None
        } else {
            Some(Box::new(Self::build_recursive(right_remainder, depth + 1, k)))
        };

        KDNode {
            point: median.0.clone(),
            id: median.1,
            left: left_node,
            right: right_node,
        }
    }

    fn distance_sq(p1: &[f64], p2: &[f64]) -> f64 {
        p1.iter()
            .zip(p2.iter())
            .map(|(a, b)| (a - b).powi(2))
            .sum()
    }

    /// Finds the nearest neighbor to the target point.
    pub fn nearest(&self, target: &[f64]) -> Option<(usize, f64)> {
        if target.len() != self.k {
            return None;
        }
        
        let mut best: Option<(&KDNode, f64)> = None;
        Self::nearest_recursive(self.root.as_deref(), target, 0, self.k, &mut best);
        
        best.map(|(node, dist_sq)| (node.id, dist_sq.sqrt()))
    }

    fn nearest_recursive<'a>(
        node_opt: Option<&'a KDNode>,
        target: &[f64],
        depth: usize,
        k: usize,
        best: &mut Option<(&'a KDNode, f64)>,
    ) {
        let node = match node_opt {
            Some(n) => n,
            None => return,
        };

        let dist_sq = Self::distance_sq(&node.point, target);
        
        match best {
            None => *best = Some((node, dist_sq)),
            Some((_, best_dist_sq)) if dist_sq < *best_dist_sq => *best = Some((node, dist_sq)),
            _ => {}
        }

        let axis = depth % k;
        let diff = target[axis] - node.point[axis];

        let (first, second) = if diff < 0.0 {
            (node.left.as_deref(), node.right.as_deref())
        } else {
            (node.right.as_deref(), node.left.as_deref())
        };

        Self::nearest_recursive(first, target, depth + 1, k, best);

        // Check if we need to search the other branch
        if let Some((_, best_dist_sq)) = best {
            if diff.powi(2) < *best_dist_sq {
                Self::nearest_recursive(second, target, depth + 1, k, best);
            }
        }
    }
}
