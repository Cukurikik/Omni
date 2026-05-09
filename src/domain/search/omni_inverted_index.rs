// omni_inverted_index.rs — Core Text Inverted Index
// Layer: Domain / Rust
//
// Implements a fast in-memory inverted index for Boolean and sparse retrieval.
// Maps terms to document IDs and their frequencies. Zero mock.

use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone)]
pub struct Posting {
    pub doc_id: String,
    pub frequency: usize,
    pub positions: Vec<usize>,
}

pub struct OmniInvertedIndex {
    index: HashMap<String, Vec<Posting>>,
    document_count: usize,
}

impl OmniInvertedIndex {
    pub fn new() -> Self {
        OmniInvertedIndex {
            index: HashMap::new(),
            document_count: 0,
        }
    }

    /// Adds a document to the inverted index.
    pub fn add_document(&mut self, doc_id: &str, tokens: &[String]) {
        self.document_count += 1;
        
        let mut term_positions: HashMap<String, Vec<usize>> = HashMap::new();
        
        for (pos, token) in tokens.iter().enumerate() {
            term_positions
                .entry(token.to_lowercase())
                .or_insert_with(Vec::new)
                .push(pos);
        }

        for (term, positions) in term_positions {
            let posting = Posting {
                doc_id: doc_id.to_string(),
                frequency: positions.len(),
                positions,
            };
            
            self.index
                .entry(term)
                .or_insert_with(Vec::new)
                .push(posting);
        }
    }

    /// Retrieves postings for a specific term.
    pub fn get_postings(&self, term: &str) -> Option<&Vec<Posting>> {
        self.index.get(&term.to_lowercase())
    }

    /// Performs a Boolean AND search across multiple terms.
    pub fn search_and(&self, query_terms: &[String]) -> HashSet<String> {
        if query_terms.is_empty() {
            return HashSet::new();
        }

        let mut results = HashSet::new();
        
        // Initialize with first term's documents
        if let Some(postings) = self.get_postings(&query_terms[0]) {
            for posting in postings {
                results.insert(posting.doc_id.clone());
            }
        } else {
            return HashSet::new(); // If first term is missing, AND fails completely
        }

        // Intersect with remaining terms
        for term in &query_terms[1..] {
            let mut current_term_docs = HashSet::new();
            
            if let Some(postings) = self.get_postings(term) {
                for posting in postings {
                    current_term_docs.insert(posting.doc_id.clone());
                }
            }
            
            results.retain(|doc_id| current_term_docs.contains(doc_id));
            
            if results.is_empty() {
                break;
            }
        }

        results
    }
}
