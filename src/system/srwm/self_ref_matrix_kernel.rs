/// @omni-layer System | @omni-source IDSIA/modern-srwm | @omni-lang Rust
/// @omni-description Self-referential matrix BLAS kernel: in-place weight update
/// with bounded norm preservation for SRWM stability.
#[derive(Debug)]
pub enum SRWMError { DimensionMismatch, NormExplosion }
pub type OmniResult<T> = Result<T, SRWMError>;

pub struct SelfRefMatrix { pub data: Vec<Vec<f64>>, pub d: usize }

impl SelfRefMatrix {
    pub fn new(d: usize) -> Self {
        let data = (0..d).map(|i| (0..d).map(|j| (((i+1)*(j+1)) as f64 * 0.01).sin() * 0.02).collect()).collect();
        Self { data, d }
    }
    pub fn forward(&self, x: &[f64]) -> OmniResult<Vec<f64>> {
        if x.len() != self.d { return Err(SRWMError::DimensionMismatch); }
        Ok((0..self.d).map(|i| (0..self.d).map(|j| self.data[i][j] * x[j]).sum::<f64>().tanh()).collect())
    }
    pub fn self_update(&mut self, x: &[f64], lr: f64, max_norm: f64) -> OmniResult<f64> {
        let h = self.forward(x)?;
        for i in 0..self.d { for j in 0..self.d { self.data[i][j] += lr * h[i] * x[j]; } }
        let norm: f64 = self.data.iter().flat_map(|r| r.iter()).map(|v| v*v).sum::<f64>().sqrt();
        if norm > max_norm {
            let scale = max_norm / norm;
            for i in 0..self.d { for j in 0..self.d { self.data[i][j] *= scale; } }
        }
        Ok(norm.min(max_norm))
    }
    pub fn spectral_radius_approx(&self) -> f64 {
        let mut x: Vec<f64> = (0..self.d).map(|i| 1.0 / (self.d as f64).sqrt()).collect();
        for _ in 0..20 {
            let y: Vec<f64> = (0..self.d).map(|i| (0..self.d).map(|j| self.data[i][j] * x[j]).sum()).collect();
            let norm: f64 = y.iter().map(|v| v*v).sum::<f64>().sqrt();
            if norm < 1e-10 { return 0.0; }
            x = y.iter().map(|v| v / norm).collect();
        }
        let y: Vec<f64> = (0..self.d).map(|i| (0..self.d).map(|j| self.data[i][j] * x[j]).sum()).collect();
        y.iter().zip(x.iter()).map(|(a,b)| a*b).sum::<f64>()
    }
}
