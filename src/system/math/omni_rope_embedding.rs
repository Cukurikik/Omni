//! Omni Rotary Positional Embedding (RoPE)
//! Implements RoPE vectors for preserving absolute and relative position information
//! across large context sequences in LLMs, ensuring zero-allocation generation.

pub struct OmniRoPE {
    pub dim: usize,
    pub base: f32,
    pub inv_freq: Vec<f32>,
}

impl OmniRoPE {
    pub fn new(dim: usize, base: f32) -> Self {
        let half_dim = dim / 2;
        let mut inv_freq = Vec::with_capacity(half_dim);
        for i in 0..half_dim {
            let p = 1.0 / base.powf((2 * i) as f32 / dim as f32);
            inv_freq.push(p);
        }
        OmniRoPE { dim, base, inv_freq }
    }

    /// Applies RoPE transformation directly to the mutable tensor slice
    /// sequence_len: the number of tokens
    /// seq_idx: the absolute position offset
    pub fn apply_rotary_emb(&self, q: &mut [f32], k: &mut [f32], sequence_len: usize, seq_idx: usize) {
        let half_dim = self.dim / 2;
        
        for pos in 0..sequence_len {
            let abs_pos = (seq_idx + pos) as f32;
            let offset = pos * self.dim;
            
            for i in 0..half_dim {
                let freq = abs_pos * self.inv_freq[i];
                let sin_val = freq.sin();
                let cos_val = freq.cos();
                
                // Query Rotation
                let q1 = q[offset + i];
                let q2 = q[offset + i + half_dim];
                q[offset + i] = q1 * cos_val - q2 * sin_val;
                q[offset + i + half_dim] = q2 * cos_val + q1 * sin_val;
                
                // Key Rotation
                let k1 = k[offset + i];
                let k2 = k[offset + i + half_dim];
                k[offset + i] = k1 * cos_val - k2 * sin_val;
                k[offset + i + half_dim] = k2 * cos_val + k1 * sin_val;
            }
        }
    }
}
