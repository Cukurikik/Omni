// omni_tree_attn_utils.rs — Tree Attention Utilities
// Layer: Compute / Rust
//
// Utility functions for manipulating tree structures, calculating node depths,
// and extracting parent-child relationships required for O(N log N) Tree Attention.

use std::collections::HashMap;

/// Represents a node in the syntax or semantic tree used for attention routing.
#[derive(Debug, Clone)]
pub struct TreeNode {
    pub id: usize,
    pub parent_id: Option<usize>,
    pub children: Vec<usize>,
    pub depth: usize,
    pub token_span: (usize, usize),
}

pub struct TreeIndex {
    nodes: HashMap<usize, TreeNode>,
    root_id: usize,
}

impl TreeIndex {
    pub fn new(root_id: usize, root_span: (usize, usize)) -> Self {
        let mut nodes = HashMap::new();
        nodes.insert(
            root_id,
            TreeNode {
                id: root_id,
                parent_id: None,
                children: Vec::new(),
                depth: 0,
                token_span: root_span,
            },
        );
        Self { nodes, root_id }
    }

    /// Adds a child node to an existing parent.
    pub fn add_child(&mut self, parent_id: usize, child_id: usize, span: (usize, usize)) -> Result<(), &'static str> {
        let parent_depth = match self.nodes.get(&parent_id) {
            Some(p) => p.depth,
            None => return Err("Parent node not found"),
        };

        let child_node = TreeNode {
            id: child_id,
            parent_id: Some(parent_id),
            children: Vec::new(),
            depth: parent_depth + 1,
            token_span: span,
        };

        if let Some(parent) = self.nodes.get_mut(&parent_id) {
            parent.children.push(child_id);
        }

        self.nodes.insert(child_id, child_node);
        Ok(())
    }

    /// Retrieves all ancestors of a given node up to the root.
    pub fn get_ancestors(&self, mut node_id: usize) -> Vec<usize> {
        let mut ancestors = Vec::new();
        while let Some(node) = self.nodes.get(&node_id) {
            if let Some(parent_id) = node.parent_id {
                ancestors.push(parent_id);
                node_id = parent_id;
            } else {
                break;
            }
        }
        ancestors
    }

    /// Extracts the adjacency matrix for tree-based masking in attention.
    pub fn build_adjacency_mask(&self, num_tokens: usize) -> Vec<Vec<bool>> {
        // Mock implementation of mask generation based on tree spans
        let mut mask = vec![vec![false; num_tokens]; num_tokens];
        // In a real implementation, nodes within the same parent span or 
        // connected paths would be marked true.
        for i in 0..num_tokens {
            mask[i][i] = true; // Identity connection
        }
        mask
    }
}
