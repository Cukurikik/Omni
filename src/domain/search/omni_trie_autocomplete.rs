// omni_trie_autocomplete.rs — Prefix Trie for Autocomplete
// Layer: Domain / Search
//
// Implements a high-performance Trie (Prefix Tree) data structure.
// Radically faster than full-text searches for exact prefix matching,
// providing O(L) insertion and lookup where L is string length. Zero mock.

use std::collections::HashMap;

#[derive(Default)]
struct TrieNode {
    children: HashMap<char, TrieNode>,
    is_end_of_word: bool,
    // Caching the most popular completions could happen here
}

pub struct OmniPrefixTrie {
    root: TrieNode,
}

impl OmniPrefixTrie {
    pub fn new() -> Self {
        OmniPrefixTrie {
            root: TrieNode::default(),
        }
    }

    /// Inserts a string into the Trie.
    pub fn insert(&mut self, word: &str) {
        let mut current = &mut self.root;
        for c in word.chars() {
            current = current.children.entry(c).or_insert_with(TrieNode::default);
        }
        current.is_end_of_word = true;
    }

    /// Checks if a word exactly exists in the Trie.
    pub fn search(&self, word: &str) -> bool {
        let mut current = &self.root;
        for c in word.chars() {
            if let Some(node) = current.children.get(&c) {
                current = node;
            } else {
                return false;
            }
        }
        current.is_end_of_word
    }

    /// Recursively collects all words under a specific node.
    fn collect_words(node: &TrieNode, prefix: &str, results: &mut Vec<String>, limit: usize) {
        if results.len() >= limit {
            return;
        }
        if node.is_end_of_word {
            results.push(prefix.to_string());
        }
        
        // Sort keys for deterministic output (optional but good for UX)
        let mut keys: Vec<&char> = node.children.keys().collect();
        keys.sort();

        for &c in keys {
            let next_prefix = format!("{}{}", prefix, c);
            Self::collect_words(&node.children[&c], &next_prefix, results, limit);
        }
    }

    /// Returns up to `limit` words that start with `prefix`.
    pub fn autocomplete(&self, prefix: &str, limit: usize) -> Vec<String> {
        let mut results = Vec::new();
        let mut current = &self.root;

        // Traverse to the end of the prefix
        for c in prefix.chars() {
            if let Some(node) = current.children.get(&c) {
                current = node;
            } else {
                // Prefix not found, no completions
                return results;
            }
        }

        // Collect descendants
        Self::collect_words(current, prefix, &mut results, limit);
        results
    }
}
