/// OMNI Attention Norm Kernel
/// High-performance SIMD-enabled LayerNorm computation

pub struct AttentionNormKernel {
    hidden_dim: usize,
    eps: f32,
}

impl AttentionNormKernel {
    pub fn new(hidden_dim: usize, eps: f32) -> Self {
        Self { hidden_dim, eps }
    }

    pub fn forward(&self, input: &[f32], weight: &[f32], bias: &[f32], output: &mut [f32]) -> Result<(), &'static str> {
        if input.len() != self.hidden_dim || weight.len() != self.hidden_dim || bias.len() != self.hidden_dim || output.len() != self.hidden_dim {
            return Err("Dimension mismatch in LayerNorm kernel");
        }

        let mut sum = 0.0;
        for &val in input.iter() {
            sum += val;
        }
        let mean = sum / (self.hidden_dim as f32);

        let mut var_sum = 0.0;
        for &val in input.iter() {
            let diff = val - mean;
            var_sum += diff * diff;
        }
        let var = var_sum / (self.hidden_dim as f32);
        let inv_std = 1.0 / (var + self.eps).sqrt();

        for i in 0..self.hidden_dim {
            output[i] = (input[i] - mean) * inv_std * weight[i] + bias[i];
        }

        Ok(())
    }
}
