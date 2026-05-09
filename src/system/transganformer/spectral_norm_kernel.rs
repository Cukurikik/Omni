/// @omni-layer System | @omni-source lucidrains/transganformer | @omni-lang Rust
/// @omni-description Spectral normalization kernel: weight matrix spectral
/// norm estimation via power iteration for GAN training stability.
use std::sync::atomic::{AtomicU64, Ordering};

#[derive(Debug)]
pub enum SpectralError { EmptyMatrix, ConvergenceFailed }
pub type OmniResult<T> = Result<T, SpectralError>;

pub struct SpectralNormKernel {
    max_iterations: usize,
    tolerance: f64,
    computations: AtomicU64,
}

impl SpectralNormKernel {
    pub fn new(max_iterations: usize, tolerance: f64) -> Self {
        Self { max_iterations, tolerance, computations: AtomicU64::new(0) }
    }

    fn l2_norm(v: &[f64]) -> f64 {
        v.iter().map(|x| x * x).sum::<f64>().sqrt()
    }

    fn normalize(v: &mut [f64]) {
        let norm = Self::l2_norm(v);
        if norm > 1e-8 { v.iter_mut().for_each(|x| *x /= norm); }
    }

    fn mat_vec(matrix: &[Vec<f64>], v: &[f64]) -> Vec<f64> {
        matrix.iter().map(|row| {
            row.iter().zip(v).map(|(a, b)| a * b).sum()
        }).collect()
    }

    fn vec_mat(v: &[f64], matrix: &[Vec<f64>]) -> Vec<f64> {
        if matrix.is_empty() { return vec![]; }
        let cols = matrix[0].len();
        (0..cols).map(|j| {
            v.iter().zip(matrix).map(|(vi, row)| vi * row[j]).sum()
        }).collect()
    }

    pub fn estimate_spectral_norm(&self, weight: &[Vec<f64>]) -> OmniResult<f64> {
        if weight.is_empty() { return Err(SpectralError::EmptyMatrix); }
        let rows = weight.len();
        let cols = weight[0].len();
        let mut u = vec![1.0 / (rows as f64).sqrt(); rows];
        let mut v = vec![1.0 / (cols as f64).sqrt(); cols];
        let mut sigma = 0.0;
        for _ in 0..self.max_iterations {
            let mut new_v = Self::vec_mat(&u, weight);
            Self::normalize(&mut new_v);
            let mut new_u = Self::mat_vec(weight, &new_v);
            let new_sigma = Self::l2_norm(&new_u);
            Self::normalize(&mut new_u);
            if (new_sigma - sigma).abs() < self.tolerance {
                self.computations.fetch_add(1, Ordering::Relaxed);
                return Ok(new_sigma);
            }
            sigma = new_sigma;
            u = new_u;
            v = new_v;
        }
        self.computations.fetch_add(1, Ordering::Relaxed);
        Ok(sigma)
    }

    pub fn normalize_weight(&self, weight: &mut [Vec<f64>]) -> OmniResult<f64> {
        let sigma = self.estimate_spectral_norm(weight)?;
        if sigma > 1e-8 {
            for row in weight.iter_mut() {
                for val in row.iter_mut() { *val /= sigma; }
            }
        }
        Ok(sigma)
    }

    pub fn total_computations(&self) -> u64 { self.computations.load(Ordering::Relaxed) }
}
