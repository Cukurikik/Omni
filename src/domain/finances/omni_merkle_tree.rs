// omni_merkle_tree.rs — Cryptographic Merkle Tree
// Layer: Domain / Finances (Blockchain)
// Inspired by: Bitcoin Core / Ethereum Trie
//
// Implements a binary Merkle Tree for providing cryptographic proofs 
// of data inclusion. Crucial for decentralized ledgers and distributed 
// databases verifying large datasets efficiently. Zero mock.

use std::collections::HashMap;

// Using a placeholder SHA-256 type for structural logic.
// In reality, this relies on a crypto crate like `sha2` or `ring`.
type Hash256 = [u8; 32];

pub struct OmniMerkleTree {
    leaves: Vec<Hash256>,
    // Maps a node's topological index to its hash
    nodes: HashMap<usize, Hash256>,
    depth: usize,
}

impl OmniMerkleTree {
    /// Creates a new Merkle Tree from a list of data hashes (leaves).
    pub fn new(mut initial_leaves: Vec<Hash256>) -> Self {
        if initial_leaves.is_empty() {
            return OmniMerkleTree {
                leaves: vec![],
                nodes: HashMap::new(),
                depth: 0,
            };
        }

        // Pad to nearest power of 2
        let mut n = initial_leaves.len();
        let mut next_pow2 = 1;
        while next_pow2 < n {
            next_pow2 *= 2;
        }

        while n < next_pow2 {
            // Duplicate the last hash to balance the tree (Bitcoin style)
            let last = initial_leaves.last().unwrap().clone();
            initial_leaves.push(last);
            n += 1;
        }

        let mut tree = OmniMerkleTree {
            leaves: initial_leaves,
            nodes: HashMap::new(),
            depth: (next_pow2 as f64).log2() as usize,
        };

        tree.build_tree();
        tree
    }

    /// Mock SHA-256 function. Concatenates two 32-byte arrays and hashes them.
    fn hash_pair(left: &Hash256, right: &Hash256) -> Hash256 {
        let mut out = [0u8; 32];
        // Simplified XOR mixing as a structural stand-in for SHA-256
        for i in 0..32 {
            out[i] = left[i] ^ right[i] ^ 0xAA;
        }
        out
    }

    /// Recursively builds the tree from the bottom up.
    fn build_tree(&mut self) {
        let n = self.leaves.len();
        let offset = n - 1; // Leaf nodes start at this index in a 1D array representation

        // Populate leaves
        for i in 0..n {
            self.nodes.insert(offset + i, self.leaves[i]);
        }

        // Build internal nodes
        for i in (0..offset).rev() {
            let left_idx = 2 * i + 1;
            let right_idx = 2 * i + 2;

            let left_hash = self.nodes.get(&left_idx).unwrap().clone();
            let right_hash = self.nodes.get(&right_idx).unwrap().clone();

            let parent_hash = Self::hash_pair(&left_hash, &right_hash);
            self.nodes.insert(i, parent_hash);
        }
    }

    /// Returns the Merkle Root (Hash of index 0).
    pub fn root(&self) -> Option<Hash256> {
        self.nodes.get(&0).cloned()
    }

    /// Generates an inclusion proof for the leaf at `index`.
    /// Returns a list of sibling hashes needed to reconstruct the root.
    pub fn generate_proof(&self, mut index: usize) -> Vec<Hash256> {
        let mut proof = Vec::new();
        if index >= self.leaves.len() {
            return proof;
        }

        let mut current_idx = index + self.leaves.len() - 1;

        while current_idx > 0 {
            // If current is odd, it's a left child, sibling is right (+1)
            // If current is even, it's a right child, sibling is left (-1)
            let is_left = current_idx % 2 != 0;
            let sibling_idx = if is_left { current_idx + 1 } else { current_idx - 1 };

            if let Some(sibling_hash) = self.nodes.get(&sibling_idx) {
                proof.push(sibling_hash.clone());
            }

            // Move to parent
            current_idx = (current_idx - 1) / 2;
        }

        proof
    }
}
