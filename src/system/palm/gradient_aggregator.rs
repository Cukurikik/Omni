// @omni-layer System | @omni-source PaddlePaddle/PALM | @omni-lang Rust
// @omni-description Multi-task gradient aggregator: weighted gradient merge for
// parallel task training in Rust with lock-free accumulation.
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug)]
pub enum GradError { Empty, Overflow }
pub type OmniResult<T> = Result<T, GradError>;

pub struct GradientAggregator {
    n_tasks: usize, d_model: usize,
    accumulated: Vec<Vec<f64>>,
    weights: Vec<f64>,
    step_count: AtomicU64,
}
impl GradientAggregator {
    pub fn new(n_tasks: usize, d_model: usize, weights: Vec<f64>) -> Self {
        Self { n_tasks, d_model, accumulated: vec![vec![0.0; d_model]; n_tasks], weights, step_count: AtomicU64::new(0) }
    }
    pub fn accumulate(&mut self, task_id: usize, gradients: &[f64]) -> OmniResult<()> {
        if task_id >= self.n_tasks { return Err(GradError::Overflow); }
        for (i, g) in gradients.iter().enumerate().take(self.d_model) {
            self.accumulated[task_id][i] += g;
        }
        Ok(())
    }
    pub fn merge(&mut self) -> OmniResult<Vec<f64>> {
        let mut merged = vec![0.0f64; self.d_model];
        for t in 0..self.n_tasks {
            let w = self.weights.get(t).copied().unwrap_or(1.0);
            for d in 0..self.d_model { merged[d] += w * self.accumulated[t][d]; }
        }
        let total_w: f64 = self.weights.iter().sum();
        for d in 0..self.d_model { merged[d] /= total_w.max(1e-8); }
        self.step_count.fetch_add(1, Ordering::Relaxed);
        for t in 0..self.n_tasks { self.accumulated[t] = vec![0.0; self.d_model]; }
        Ok(merged)
    }
    pub fn grad_norm(grads: &[f64]) -> f64 { grads.iter().map(|g| g*g).sum::<f64>().sqrt() }
}
