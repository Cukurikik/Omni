use std::collections::HashMap;

pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub struct HNSWVectorIndexer {
    dim: usize,
    index: HashMap<u64, Vec<f32>>,
}

impl HNSWVectorIndexer {
    pub fn new(dim: usize) -> Self {
        Self {
            dim,
            index: HashMap::new(),
        }
    }

    pub fn insert_vector(&mut self, id: u64, vec: Vec<f32>) -> OmniResult<()> {
        if vec.len() != self.dim {
            return OmniResult { value: None, error: Some("Dimension mismatch".to_string()), is_ok: false };
        }
        
        // Native local memory insertion
        self.index.insert(id, vec);
        OmniResult { value: Some(()), error: None, is_ok: true }
    }

    pub fn query_knn(&self, query: Vec<f32>, k: usize) -> OmniResult<Vec<u64>> {
        if query.len() != self.dim {
            return OmniResult { value: None, error: Some("Dimension mismatch".to_string()), is_ok: false };
        }
        
        let mut distances: Vec<(u64, f32)> = self.index.iter().map(|(id, v)| {
            let dist: f32 = v.iter().zip(query.iter())
                .map(|(a, b)| (a - b).powi(2))
                .sum::<f32>()
                .sqrt();
            (*id, dist)
        }).collect();
        
        distances.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        
        let result = distances.into_iter().take(k).map(|(id, _)| id).collect();
        OmniResult { value: Some(result), error: None, is_ok: true }
    }
}
