// omni_bm25_optimizer.rs — BM25 Hyperparameter Tuning
// Layer: Domain / Rust
//
// Grid search optimization algorithm to find the optimal k1 and b parameters
// for the BM25 model based on a validation set of queries and relevant documents.

use std::collections::HashMap;

// Mock-free interface expected from the BM25 implementation
pub trait BM25Scorer {
    fn fit(&mut self, k1: f64, b: f64, corpus: &[Vec<String>]);
    fn top_k(&self, query: &[String], k: usize) -> Vec<(usize, f64)>;
}

pub struct OmniBM25Optimizer;

impl OmniBM25Optimizer {
    /// Evaluates the Mean Reciprocal Rank (MRR) of the model given current params.
    fn evaluate_mrr<T: BM25Scorer>(
        model: &mut T,
        k1: f64,
        b: f64,
        corpus: &[Vec<String>],
        validation_queries: &[(Vec<String>, usize)] // Query tokens -> Relevant Doc Index
    ) -> f64 {
        model.fit(k1, b, corpus);
        
        let mut total_rr = 0.0;
        
        for (query, expected_doc_idx) in validation_queries {
            // Retrieve top 100 candidates
            let hits = model.top_k(query, 100);
            
            let mut rank = 0;
            for (i, (doc_idx, _)) in hits.iter().enumerate() {
                if doc_idx == expected_doc_idx {
                    rank = i + 1;
                    break;
                }
            }
            
            if rank > 0 {
                total_rr += 1.0 / (rank as f64);
            }
        }
        
        if validation_queries.is_empty() {
            0.0
        } else {
            total_rr / (validation_queries.len() as f64)
        }
    }

    /// Performs a grid search over typical k1 and b ranges to maximize MRR.
    pub fn optimize<T: BM25Scorer>(
        model: &mut T,
        corpus: &[Vec<String>],
        validation_queries: &[(Vec<String>, usize)]
    ) -> (f64, f64, f64) { // Returns (Best k1, Best b, Best MRR)
        
        let k1_range = [0.5, 0.8, 1.2, 1.5, 2.0];
        let b_range = [0.3, 0.5, 0.75, 0.9, 1.0];
        
        let mut best_k1 = 1.2;
        let mut best_b = 0.75;
        let mut best_mrr = -1.0;

        for &k1 in &k1_range {
            for &b in &b_range {
                let mrr = Self::evaluate_mrr(model, k1, b, corpus, validation_queries);
                
                if mrr > best_mrr {
                    best_mrr = mrr;
                    best_k1 = k1;
                    best_b = b;
                }
            }
        }

        (best_k1, best_b, best_mrr)
    }
}
