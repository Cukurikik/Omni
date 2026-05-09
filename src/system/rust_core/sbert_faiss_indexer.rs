use std::collections::HashMap;

/// OMNI SBERT FAISS Indexer
/// High-performance vector similarity search for dense embeddings.

pub struct SbertFaissIndexer {
    dim: usize,
    vectors: Vec<Vec<f32>>,
    doc_ids: Vec<String>,
}

impl SbertFaissIndexer {
    pub fn new(dim: usize) -> Self {
        Self {
            dim,
            vectors: Vec::new(),
            doc_ids: Vec::new(),
        }
    }

    pub fn add_vector(&mut self, doc_id: String, vector: Vec<f32>) -> Result<(), &'static str> {
        if vector.len() != self.dim {
            return Err("Vector dimension does not match index dimension");
        }
        self.vectors.push(vector);
        self.doc_ids.push(doc_id);
        Ok(())
    }

    pub fn search(&self, query_vector: &[f32], top_k: usize) -> Result<Vec<(String, f32)>, &'static str> {
        if query_vector.len() != self.dim {
            return Err("Query dimension does not match index dimension");
        }

        let mut results: Vec<(String, f32)> = self.vectors
            .iter()
            .enumerate()
            .map(|(i, vec)| {
                let score = Self::cosine_similarity(query_vector, vec);
                (self.doc_ids[i].clone(), score)
            })
            .collect();

        // Sort descending by score
        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        Ok(results.into_iter().take(top_k).collect())
    }

    fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
        let mut dot = 0.0;
        let mut norm_a = 0.0;
        let mut norm_b = 0.0;

        for i in 0..a.len() {
            dot += a[i] * b[i];
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
        }

        if norm_a == 0.0 || norm_b == 0.0 {
            0.0
        } else {
            dot / (norm_a.sqrt() * norm_b.sqrt())
        }
    }
}
