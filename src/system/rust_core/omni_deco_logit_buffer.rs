// Omni DeCo Logit Buffer (Rust)
// System Layer: Memory-safe logit buffer for dynamic correction.
// Ref: zjunlp/Deco — ICLR 2025
pub struct LogitBuffer { data: Vec<f64>, vocab_size: usize }
impl LogitBuffer {
    pub fn new(vocab: usize) -> Self { Self { data: vec![0.0; vocab], vocab_size: vocab } }
    pub fn apply_penalty(&mut self, indices: &[usize], penalty: f64) {
        for &i in indices { if i < self.vocab_size { self.data[i] -= penalty; } }
    }
    pub fn argmax(&self) -> usize {
        self.data.iter().enumerate().max_by(|a, b| a.1.partial_cmp(b.1).unwrap()).map(|(i, _)| i).unwrap_or(0)
    }
}
