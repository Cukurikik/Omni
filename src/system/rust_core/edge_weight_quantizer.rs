/// OMNI Edge Weight Quantizer
/// Rust-based fast INT8 quantization for edge-to-server FL communication.

pub struct EdgeWeightQuantizer {
    scale: f32,
    zero_point: i8,
}

impl EdgeWeightQuantizer {
    pub fn new() -> Self {
        Self {
            scale: 0.0,
            zero_point: 0,
        }
    }

    pub fn compute_scale_zero_point(&mut self, weights: &[f32]) {
        if weights.is_empty() { return; }
        
        let mut min_val = weights[0];
        let mut max_val = weights[0];
        
        for &w in weights {
            if w < min_val { min_val = w; }
            if w > max_val { max_val = w; }
        }
        
        // Ensure zero is representable
        min_val = min_val.min(0.0);
        max_val = max_val.max(0.0);
        
        self.scale = (max_val - min_val) / 255.0;
        self.zero_point = (-128.0 - min_val / self.scale).round() as i8;
    }

    pub fn quantize(&self, weights: &[f32]) -> Result<Vec<i8>, &'static str> {
        if self.scale == 0.0 {
            return Err("Scale is zero, call compute_scale_zero_point first");
        }
        
        let mut quantized = Vec::with_capacity(weights.len());
        for &w in weights {
            let q = (w / self.scale).round() as i32 + self.zero_point as i32;
            let q_clamped = q.max(-128).min(127) as i8;
            quantized.push(q_clamped);
        }
        
        Ok(quantized)
    }
}
