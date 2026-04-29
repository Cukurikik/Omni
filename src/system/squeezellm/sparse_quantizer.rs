pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub struct SqueezeSparseQuantizer {
    pub sparsity_threshold: f32,
}

impl SqueezeSparseQuantizer {
    pub fn quantize(&self, weights: &[f32]) -> OmniResult<Vec<i8>> {
        if weights.is_empty() {
            return OmniResult { value: None, error: Some("Empty weights".to_string()), is_ok: false };
        }
        
        let mut quantized = Vec::with_capacity(weights.len());
        for &w in weights {
            if w.abs() < self.sparsity_threshold {
                quantized.push(0);
            } else {
                // simple 8-bit mapping
                let q = (w * 127.0).clamp(-128.0, 127.0) as i8;
                quantized.push(q);
            }
        }
        
        OmniResult { value: Some(quantized), error: None, is_ok: true }
    }
}
