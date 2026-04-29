/// OMNI PATTERN CLASSIFICATION: SVM Radial Basis Function (RBF) Kernel
/// Rust zero-copy memory implementation for fast vector similarity math.
/// Source: rasbt/pattern_classification

#[derive(Debug)]
pub enum KernelError {
    DimensionMismatch,
    ZeroGamma,
}

pub struct SVMKernel;

impl SVMKernel {
    /// Computes the RBF (Gaussian) kernel between two vectors: K(x, x') = exp(-gamma * ||x - x'||^2)
    pub fn compute_rbf(vec_a: &[f64], vec_b: &[f64], gamma: f64) -> Result<f64, KernelError> {
        if vec_a.len() != vec_b.len() {
            return Err(KernelError::DimensionMismatch);
        }
        
        if gamma == 0.0 {
            return Err(KernelError::ZeroGamma);
        }

        let mut squared_distance = 0.0;
        
        // Use iterators for auto-vectorization by LLVM
        for (a, b) in vec_a.iter().zip(vec_b.iter()) {
            let diff = a - b;
            squared_distance += diff * diff;
        }

        let rbf_value = (-gamma * squared_distance).exp();
        
        Ok(rbf_value)
    }
    
    /// Computes the linear kernel: K(x, x') = x^T * x'
    pub fn compute_linear(vec_a: &[f64], vec_b: &[f64]) -> Result<f64, KernelError> {
         if vec_a.len() != vec_b.len() {
            return Err(KernelError::DimensionMismatch);
        }
        
        let dot_product: f64 = vec_a.iter().zip(vec_b.iter()).map(|(a, b)| a * b).sum();
        
        Ok(dot_product)
    }
}
