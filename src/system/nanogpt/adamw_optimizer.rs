/// @omni-layer System | @omni-source karpathy/nanoGPT | @omni-lang Rust
/// @omni-description AdamW optimizer kernel: weight decay decoupled from gradient,
/// bias correction, and gradient clipping in Rust.
#[derive(Debug)]
pub enum OptError { EmptyParams, NaN }
pub type OmniResult<T> = Result<T, OptError>;

pub struct AdamWState { pub m: Vec<f64>, pub v: Vec<f64>, pub step: u64 }

pub struct AdamWOptimizer {
    pub lr: f64, pub beta1: f64, pub beta2: f64,
    pub eps: f64, pub weight_decay: f64, pub max_grad_norm: f64,
}
impl AdamWOptimizer {
    pub fn new(lr: f64) -> Self {
        Self { lr, beta1: 0.9, beta2: 0.999, eps: 1e-8, weight_decay: 0.01, max_grad_norm: 1.0 }
    }
    pub fn init_state(&self, n: usize) -> AdamWState {
        AdamWState { m: vec![0.0; n], v: vec![0.0; n], step: 0 }
    }
    pub fn clip_grad(&self, grads: &mut [f64]) -> f64 {
        let norm: f64 = grads.iter().map(|g| g*g).sum::<f64>().sqrt();
        if norm > self.max_grad_norm {
            let scale = self.max_grad_norm / norm;
            for g in grads.iter_mut() { *g *= scale; }
        }
        norm
    }
    pub fn step(&self, params: &mut [f64], grads: &mut [f64], state: &mut AdamWState) -> OmniResult<f64> {
        if params.is_empty() { return Err(OptError::EmptyParams); }
        let grad_norm = self.clip_grad(grads);
        state.step += 1;
        let bc1 = 1.0 - self.beta1.powi(state.step as i32);
        let bc2 = 1.0 - self.beta2.powi(state.step as i32);
        for i in 0..params.len() {
            state.m[i] = self.beta1 * state.m[i] + (1.0 - self.beta1) * grads[i];
            state.v[i] = self.beta2 * state.v[i] + (1.0 - self.beta2) * grads[i] * grads[i];
            let m_hat = state.m[i] / bc1;
            let v_hat = state.v[i] / bc2;
            params[i] -= self.lr * (m_hat / (v_hat.sqrt() + self.eps) + self.weight_decay * params[i]);
        }
        Ok(grad_norm)
    }
}
