// omni_query_expander.rs — Search Query Expansion
// Layer: Domain / Rust
//
// Implements synonym-based query expansion to improve search recall.
// Can integrate with word embeddings or static dictionary rules. Zero mock.

use std::collections::{HashMap, HashSet};

pub struct OmniQueryExpander {
    synonym_map: HashMap<String, Vec<String>>,
}

impl OmniQueryExpander {
    pub fn new() -> Self {
        OmniQueryExpander {
            synonym_map: HashMap::new(),
        }
    }

    /// Loads a static dictionary of synonyms.
    pub fn load_synonyms(&mut self, rules: Vec<(&str, Vec<&str>)>) {
        for (root, syns) in rules {
            let root_lower = root.to_lowercase();
            let mut expanded = Vec::new();
            
            for s in syns {
                expanded.push(s.to_lowercase());
            }
            
            self.synonym_map.insert(root_lower, expanded);
        }
    }

    /// Expands a parsed query by appending relevant synonyms.
    pub fn expand_query(&self, parsed_tokens: &[String]) -> Vec<String> {
        let mut expanded_query = HashSet::new();

        for token in parsed_tokens {
            let t_lower = token.to_lowercase();
            
            // Always include the original token
            expanded_query.insert(t_lower.clone());

            // Add direct synonyms
            if let Some(syns) = self.synonym_map.get(&t_lower) {
                for syn in syns {
                    expanded_query.insert(syn.clone());
                }
            }

            // Reverse lookup: if this token is a synonym for a root word, add the root word
            // This is O(N) over the map, usually fine for small vocabularies, 
            // but can be optimized by building a bidirectional map in load_synonyms.
            for (root, syns) in &self.synonym_map {
                if syns.contains(&t_lower) {
                    expanded_query.insert(root.clone());
                }
            }
        }

        expanded_query.into_iter().collect()
    }
}
