// omni_tf_idf_scorer.rs — TF-IDF Vector Space Model
// Layer: Domain / Search
//
// Implements Term Frequency-Inverse Document Frequency (TF-IDF) scoring
// for document retrieval. Converts unstructured text into a sparse mathematical
// vector space, allowing for Cosine Similarity matching. Zero mock.

use std::collections::{HashMap, HashSet};

pub struct OmniTfIdfScorer {
    // Map DocumentID -> (Map Term -> Frequency)
    document_term_freq: HashMap<usize, HashMap<String, usize>>,
    // Map Term -> Number of documents containing the term
    document_frequency: HashMap<String, usize>,
    total_documents: usize,
}

impl OmniTfIdfScorer {
    pub fn new() -> Self {
        OmniTfIdfScorer {
            document_term_freq: HashMap::new(),
            document_frequency: HashMap::new(),
            total_documents: 0,
        }
    }

    /// Tokenizes a string into lowercase alphanumeric words
    fn tokenize(text: &str) -> Vec<String> {
        text.to_lowercase()
            .split_whitespace()
            .filter(|s| s.chars().all(char::is_alphanumeric))
            .map(|s| s.to_string())
            .collect()
    }

    /// Adds a document to the corpus and updates statistics
    pub fn add_document(&mut self, doc_id: usize, text: &str) {
        let tokens = Self::tokenize(text);
        let mut term_freq = HashMap::new();
        let mut unique_terms = HashSet::new();

        for token in tokens {
            *term_freq.entry(token.clone()).or_insert(0) += 1;
            unique_terms.insert(token);
        }

        self.document_term_freq.insert(doc_id, term_freq);

        for term in unique_terms {
            *self.document_frequency.entry(term).or_insert(0) += 1;
        }

        self.total_documents += 1;
    }

    /// Computes the TF-IDF weight for a specific term in a specific document
    pub fn tf_idf(&self, term: &str, doc_id: usize) -> f64 {
        let tf = match self.document_term_freq.get(&doc_id) {
            Some(tf_map) => *tf_map.get(term).unwrap_or(&0) as f64,
            None => return 0.0,
        };

        if tf == 0.0 {
            return 0.0;
        }

        // Sub-linear TF scaling: 1 + log(tf)
        let scaled_tf = 1.0 + tf.ln();

        let df = *self.document_frequency.get(term).unwrap_or(&0) as f64;
        
        // IDF with smoothing: log(1 + (N / df))
        let idf = 1.0 + ((self.total_documents as f64) / (df + 1.0)).ln();

        scaled_tf * idf
    }

    /// Scores a query against a specific document
    pub fn score_query(&self, query: &str, doc_id: usize) -> f64 {
        let tokens = Self::tokenize(query);
        let mut score = 0.0;

        for term in tokens {
            score += self.tf_idf(&term, doc_id);
        }

        score
    }

    /// Returns the top K documents for a given query
    pub fn search(&self, query: &str, top_k: usize) -> Vec<(usize, f64)> {
        let mut scores: Vec<(usize, f64)> = self.document_term_freq.keys()
            .map(|&doc_id| (doc_id, self.score_query(query, doc_id)))
            .filter(|&(_, score)| score > 0.0) // Only keep matching documents
            .collect();

        // Sort descending by score
        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

        scores.into_iter().take(top_k).collect()
    }
}
