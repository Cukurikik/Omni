// Omni SLED Logit Evolution Buffer (Rust)
// System: Memory-safe buffer for logit evolution decoding.
// Ref: JayZhang42/SLED
pub struct SledBuffer { early: Vec<f64>, late: Vec<f64> }
impl SledBuffer {
    pub fn new(size: usize) -> Self { Self { early: vec![0.0; size], late: vec![0.0; size] } }
    pub fn evolve(&self, alpha: f64) -> Vec<f64> {
        self.late.iter().zip(self.early.iter())
            .map(|(l, e)| l + alpha * (l - e)).collect()
    }
    pub fn argmax(v: &[f64]) -> usize {
        v.iter().enumerate().max_by(|a, b| a.1.partial_cmp(b.1).unwrap()).map(|(i,_)| i).unwrap_or(0)
    }
}
