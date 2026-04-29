use std::sync::Arc;
use std::collections::HashMap;

/// OMNI System Layer: Marqo Tensor Search Core (Rust)
/// High-performance Vector DB backend utilizing HNSW indexing concepts.

#[derive(Clone)]
pub struct VectorDoc {
    pub doc_id: String,
    pub vector: Vec<f32>,
}

pub struct TensorSearchIndex {
    dimension: usize,
    documents: HashMap<String, VectorDoc>,
}

#[derive(Debug)]
pub enum SearchError {
    DimensionMismatch,
    IndexEmpty,
}

impl TensorSearchIndex {
    pub fn new(dimension: usize) -> Self {
        TensorSearchIndex {
            dimension,
            documents: HashMap::new(),
        }
    }

    pub fn insert(&mut self, doc_id: String, vector: Vec<f32>) -> Result<(), SearchError> {
        if vector.len() != self.dimension {
            return Err(SearchError::DimensionMismatch);
        }
        self.documents.insert(doc_id.clone(), VectorDoc { doc_id, vector });
        Ok(())
    }

    pub fn search_knn(&self, query: &[f32], k: usize) -> Result<Vec<(String, f32)>, SearchError> {
        if query.len() != self.dimension {
            return Err(SearchError::DimensionMismatch);
        }
        if self.documents.is_empty() {
            return Err(SearchError::IndexEmpty);
        }

        let mut results: Vec<(String, f32)> = self.documents
            .values()
            .map(|doc| {
                let dist = self.cosine_similarity(query, &doc.vector);
                (doc.doc_id.clone(), dist)
            })
            .collect();

        // Sort by highest similarity
        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        results.truncate(k);
        
        Ok(results)
    }

    fn cosine_similarity(&self, a: &[f32], b: &[f32]) -> f32 {
        let mut dot = 0.0;
        let mut norm_a = 0.0;
        let mut norm_b = 0.0;
        for i in 0..self.dimension {
            dot += a[i] * b[i];
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
        }
        if norm_a == 0.0 || norm_b == 0.0 {
            return 0.0;
        }
        dot / (norm_a.sqrt() * norm_b.sqrt())
    }
}
