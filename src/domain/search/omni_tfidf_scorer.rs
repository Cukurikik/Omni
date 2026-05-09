// omni_tfidf_scorer.rs — TF-IDF Scoring Engine
// Layer: Domain / Rust
//
// Implements Term Frequency-Inverse Document Frequency (TF-IDF) scoring
// across a corpus. Fully realized mathematical algorithm, zero mock.

use std::collections::HashMap;

pub struct OmniTfidfScorer {
    doc_count: usize,
    document_frequencies: HashMap<String, usize>,
    idf_cache: HashMap<String, f64>,
}

impl OmniTfidfScorer {
    pub fn new() -> Self {
        OmniTfidfScorer {
            doc_count: 0,
            document_frequencies: HashMap::new(),
            idf_cache: HashMap::new(),
        }
    }

    /// Fits the IDF model over a pre-tokenized corpus.
    pub fn fit(&mut self, corpus: &[Vec<String>]) {
        self.doc_count = corpus.len();
        self.document_frequencies.clear();
        self.idf_cache.clear();

        for doc in corpus {
            let mut unique_terms = HashMap::new();
            for term in doc {
                unique_terms.insert(term.to_lowercase(), true);
            }
            
            for (term, _) in unique_terms {
                *self.document_frequencies.entry(term).or_insert(0) += 1;
            }
        }

        // Calculate IDF: log_e((1 + N) / (1 + df)) + 1
        for (term, &df) in &self.document_frequencies {
            let idf = ((1.0 + self.doc_count as f64) / (1.0 + df as f64)).ln() + 1.0;
            self.idf_cache.insert(term.clone(), idf);
        }
    }

    /// Transforms a single pre-tokenized document into a TF-IDF vector.
    /// Returns a Hashmap of Token -> Score, effectively a sparse vector.
    pub fn transform(&self, document: &[String]) -> HashMap<String, f64> {
        let mut tf_counts: HashMap<String, usize> = HashMap::new();
        let doc_length = document.len();

        for token in document {
            *tf_counts.entry(token.to_lowercase()).or_insert(0) += 1;
        }

        let mut tfidf_vector = HashMap::new();
        let mut norm_sq = 0.0;

        for (term, &count) in &tf_counts {
            // Default IDF is just ln(1+N) + 1 if not in corpus
            let default_idf = ((1.0 + self.doc_count as f64) / 1.0).ln() + 1.0;
            let idf = self.idf_cache.get(term).unwrap_or(&default_idf);
            
            let tf = count as f64 / (doc_length as f64).max(1.0);
            let tfidf = tf * idf;
            
            tfidf_vector.insert(term.clone(), tfidf);
            norm_sq += tfidf * tfidf;
        }

        // L2 Normalization
        let norm = norm_sq.sqrt();
        if norm > 0.0 {
            for (_, val) in tfidf_vector.iter_mut() {
                *val /= norm;
            }
        }

        tfidf_vector
    }
}
