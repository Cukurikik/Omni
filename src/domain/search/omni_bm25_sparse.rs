// omni_bm25_sparse.rs — BM25 Sparse Information Retrieval
// Layer: Domain / Rust
//
// Implements Okapi BM25 scoring algorithm for fast sparse text retrieval.
// Fully operational math, zero-mock implementation.

use std::collections::HashMap;

pub struct OmniBM25 {
    k1: f64,
    b: f64,
    doc_count: usize,
    avg_doc_len: f64,
    doc_lengths: Vec<usize>,
    idf_cache: HashMap<String, f64>,
    term_frequencies: Vec<HashMap<String, usize>>,
}

impl OmniBM25 {
    /// Initializes the BM25 model with standard parameters.
    pub fn new(k1: f64, b: f64) -> Self {
        OmniBM25 {
            k1,
            b,
            doc_count: 0,
            avg_doc_len: 0.0,
            doc_lengths: Vec::new(),
            idf_cache: HashMap::new(),
            term_frequencies: Vec::new(),
        }
    }

    /// Ingests a corpus of documents (already tokenized).
    pub fn fit(&mut self, corpus: &[Vec<String>]) {
        self.doc_count = corpus.len();
        let mut total_len = 0;
        let mut doc_freqs: HashMap<String, usize> = HashMap::new();

        for doc in corpus {
            let len = doc.len();
            self.doc_lengths.push(len);
            total_len += len;

            let mut tf: HashMap<String, usize> = HashMap::new();
            for term in doc {
                *tf.entry(term.clone()).or_insert(0) += 1;
            }
            
            for term in tf.keys() {
                *doc_freqs.entry(term.clone()).or_insert(0) += 1;
            }
            
            self.term_frequencies.push(tf);
        }

        self.avg_doc_len = if self.doc_count > 0 {
            total_len as f64 / self.doc_count as f64
        } else {
            0.0
        };

        // Compute IDF
        for (term, freq) in doc_freqs {
            let idf = ((self.doc_count as f64 - freq as f64 + 0.5) / (freq as f64 + 0.5) + 1.0).ln();
            self.idf_cache.insert(term, idf);
        }
    }

    /// Scores a query against all documents.
    pub fn get_scores(&self, query: &[String]) -> Vec<f64> {
        let mut scores = vec![0.0; self.doc_count];

        for term in query {
            if let Some(&idf) = self.idf_cache.get(term) {
                for i in 0..self.doc_count {
                    if let Some(&tf) = self.term_frequencies[i].get(term) {
                        let tf = tf as f64;
                        let doc_len = self.doc_lengths[i] as f64;
                        let numerator = tf * (self.k1 + 1.0);
                        let denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len));
                        scores[i] += idf * (numerator / denominator);
                    }
                }
            }
        }
        scores
    }

    /// Returns the top-k document indices based on BM25 scores.
    pub fn top_k(&self, query: &[String], k: usize) -> Vec<(usize, f64)> {
        let scores = self.get_scores(query);
        let mut indexed_scores: Vec<(usize, f64)> = scores.into_iter().enumerate().collect();
        
        indexed_scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        indexed_scores.into_iter().take(k).collect()
    }
}
