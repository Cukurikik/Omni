// Omni RS SpatioTemporal VLM Bridge (Rust)
// Based on Awesome-RS-SpatioTemporal-VLMs
// Memory-safe struct definitions for temporal remote sensing arrays.

#[derive(Debug, PartialEq)]
pub enum RSError {
    DimensionMismatch,
    EmptyBuffer,
}

pub struct SpatioTemporalTensor {
    pub width: usize,
    pub height: usize,
    pub temporal_frames: usize,
    pub data: Vec<f32>,
}

impl SpatioTemporalTensor {
    pub fn new(w: usize, h: usize, t: usize, initial_val: f32) -> Result<Self, RSError> {
        if w == 0 || h == 0 || t == 0 {
            return Err(RSError::EmptyBuffer);
        }
        let total_size = w * h * t;
        Ok(Self {
            width: w,
            height: h,
            temporal_frames: t,
            data: vec![initial_val; total_size],
        })
    }

    pub fn compute_temporal_mean(&self) -> Result<Vec<f32>, RSError> {
        let spatial_size = self.width * self.height;
        let mut means = vec![0.0; spatial_size];

        for t in 0..self.temporal_frames {
            let offset = t * spatial_size;
            for i in 0..spatial_size {
                means[i] += self.data[offset + i] / (self.temporal_frames as f32);
            }
        }
        
        Ok(means)
    }
}
