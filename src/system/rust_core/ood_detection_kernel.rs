/// OMNI Out-Of-Distribution Detection Kernel
/// Rust-based fast covariance matrix evaluation for Mahalanobis distances.

pub struct OodDetectionKernel {
    feature_dim: usize,
    inv_covariance_matrix: Vec<f32>, // Flattened
    class_means: Vec<Vec<f32>>,
}

impl OodDetectionKernel {
    pub fn new(feature_dim: usize, num_classes: usize) -> Self {
        Self {
            feature_dim,
            inv_covariance_matrix: vec![1.0; feature_dim * feature_dim], // Identity for now
            class_means: vec![vec![0.0; feature_dim]; num_classes],
        }
    }

    pub fn set_covariance(&mut self, inv_cov: Vec<f32>) -> Result<(), &'static str> {
        if inv_cov.len() != self.feature_dim * self.feature_dim {
            return Err("Invalid covariance matrix dimensions");
        }
        self.inv_covariance_matrix = inv_cov;
        Ok(())
    }

    pub fn compute_mahalanobis_distance(&self, features: &[f32], class_idx: usize) -> Result<f32, &'static str> {
        if features.len() != self.feature_dim {
            return Err("Feature dimension mismatch");
        }
        if class_idx >= self.class_means.len() {
            return Err("Class index out of bounds");
        }

        let mean = &self.class_means[class_idx];
        let mut diff = vec![0.0; self.feature_dim];
        for i in 0..self.feature_dim {
            diff[i] = features[i] - mean[i];
        }

        let mut dist = 0.0;
        for i in 0..self.feature_dim {
            let mut temp = 0.0;
            for j in 0..self.feature_dim {
                temp += diff[j] * self.inv_covariance_matrix[i * self.feature_dim + j];
            }
            dist += temp * diff[i];
        }

        Ok(dist)
    }
}
