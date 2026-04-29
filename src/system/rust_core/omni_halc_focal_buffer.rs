// Omni HALC Focal Grounding Buffer (Rust)
// Ref: BillChan226/HALC — ICML'24
pub struct FocalBuffer { logits: Vec<f64>, focal: Vec<f64>, alpha: f64 }
impl FocalBuffer {
    pub fn new(n: usize, alpha: f64) -> Self {
        Self { logits: vec![0.0; n], focal: vec![0.0; n], alpha }
    }
    pub fn contrast(&self) -> Vec<f64> {
        self.logits.iter().zip(self.focal.iter())
            .map(|(o, f)| o + self.alpha * (f - o)).collect()
    }
    pub fn argmax(v: &[f64]) -> usize {
        v.iter().enumerate().max_by(|a, b| a.1.partial_cmp(b.1).unwrap())
            .map(|(i, _)| i).unwrap_or(0)
    }
}
