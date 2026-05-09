// omni_tree_attention.rs — Tree-based Hierarchical Attention
// Inspired by: Erwin (Tree-based Hierarchical Transformer)
// Layer: Compute / Rust
//
// Implements hierarchical tree attention for large-scale physical systems,
// enabling O(N log N) scaling by aggregating spatial features at multiple scales.

use std::sync::Arc;

#[derive(Debug, Clone)]
pub struct TreeNode {
    pub id: usize,
    pub children: Vec<usize>,
    pub parent: Option<usize>,
    pub level: usize,
    // Bounding box or spatial extent
    pub spatial_bounds: [f32; 6], // xmin, xmax, ymin, ymax, zmin, zmax
}

#[derive(Debug)]
pub struct TreeHierarchy {
    pub nodes: Vec<TreeNode>,
    pub max_levels: usize,
    pub leaf_count: usize,
}

impl TreeHierarchy {
    pub fn new(nodes: Vec<TreeNode>) -> Self {
        let mut max_levels = 0;
        let mut leaf_count = 0;
        
        for node in &nodes {
            if node.level > max_levels {
                max_levels = node.level;
            }
            if node.children.is_empty() {
                leaf_count += 1;
            }
        }
        
        Self {
            nodes,
            max_levels,
            leaf_count,
        }
    }

    /// Retrieve ancestors of a node up to the root
    pub fn get_ancestors(&self, node_id: usize) -> Vec<usize> {
        let mut ancestors = Vec::new();
        let mut current = self.nodes[node_id].parent;
        
        while let Some(parent_id) = current {
            ancestors.push(parent_id);
            current = self.nodes[parent_id].parent;
        }
        
        ancestors
    }
}

/// Simulated output tensor type for Rust compute layer
pub struct Tensor {
    pub data: Vec<f32>,
    pub shape: Vec<usize>,
}

pub struct TreeAttentionEngine {
    pub hidden_dim: usize,
    pub num_heads: usize,
}

impl TreeAttentionEngine {
    pub fn new(hidden_dim: usize, num_heads: usize) -> Self {
        Self {
            hidden_dim,
            num_heads,
        }
    }

    /// Bottom-up pass: Aggregate features from children to parents
    pub fn bottom_up_aggregation(&self, tree: &TreeHierarchy, leaf_features: &Tensor) -> Tensor {
        let n_nodes = tree.nodes.len();
        let mut aggregated = vec![0.0f32; n_nodes * self.hidden_dim];
        
        // Copy leaf features
        for i in 0..tree.leaf_count {
            let start = i * self.hidden_dim;
            let end = start + self.hidden_dim;
            aggregated[start..end].copy_from_slice(&leaf_features.data[start..end]);
        }
        
        // Process level by level, bottom up
        for level in (0..tree.max_levels).rev() {
            for node in &tree.nodes {
                if node.level == level && !node.children.is_empty() {
                    // Aggregate children (mean pooling for simplicity)
                    let parent_offset = node.id * self.hidden_dim;
                    for &child_id in &node.children {
                        let child_offset = child_id * self.hidden_dim;
                        for d in 0..self.hidden_dim {
                            aggregated[parent_offset + d] += aggregated[child_offset + d];
                        }
                    }
                    
                    // Normalize
                    let count = node.children.len() as f32;
                    for d in 0..self.hidden_dim {
                        aggregated[parent_offset + d] /= count;
                    }
                }
            }
        }
        
        Tensor {
            data: aggregated,
            shape: vec![n_nodes, self.hidden_dim],
        }
    }

    /// Top-down pass: Broadcast contextual information down the tree
    pub fn top_down_broadcast(&self, tree: &TreeHierarchy, aggregated_features: &Tensor) -> Tensor {
        let n_nodes = tree.nodes.len();
        let mut contextualized = vec![0.0f32; n_nodes * self.hidden_dim];
        
        // Root nodes get their own aggregated feature
        for node in &tree.nodes {
            if node.parent.is_none() {
                let offset = node.id * self.hidden_dim;
                contextualized[offset..offset + self.hidden_dim]
                    .copy_from_slice(&aggregated_features.data[offset..offset + self.hidden_dim]);
            }
        }
        
        // Process level by level, top down
        for level in 1..=tree.max_levels {
            for node in &tree.nodes {
                if node.level == level {
                    if let Some(parent_id) = node.parent {
                        let node_offset = node.id * self.hidden_dim;
                        let parent_offset = parent_id * self.hidden_dim;
                        
                        // Combine node feature with parent context (simple addition here)
                        for d in 0..self.hidden_dim {
                            contextualized[node_offset + d] = 
                                aggregated_features.data[node_offset + d] + 
                                contextualized[parent_offset + d];
                        }
                    }
                }
            }
        }
        
        Tensor {
            data: contextualized,
            shape: vec![n_nodes, self.hidden_dim],
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tree_aggregation() {
        let nodes = vec![
            TreeNode { id: 0, children: vec![1, 2], parent: None, level: 0, spatial_bounds: [0.0; 6] },
            TreeNode { id: 1, children: vec![], parent: Some(0), level: 1, spatial_bounds: [0.0; 6] },
            TreeNode { id: 2, children: vec![], parent: Some(0), level: 1, spatial_bounds: [0.0; 6] },
        ];
        
        let tree = TreeHierarchy::new(nodes);
        let engine = TreeAttentionEngine::new(2, 1);
        
        let leaf_features = Tensor {
            data: vec![
                0.0, 0.0, // Root (empty initially)
                2.0, 4.0, // Leaf 1
                6.0, 8.0, // Leaf 2
            ],
            shape: vec![3, 2],
        };
        
        let aggregated = engine.bottom_up_aggregation(&tree, &leaf_features);
        
        // Root should be mean of leaves: (2+6)/2=4, (4+8)/2=6
        assert_eq!(aggregated.data[0], 4.0);
        assert_eq!(aggregated.data[1], 6.0);
    }
}
