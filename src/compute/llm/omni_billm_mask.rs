use std::error::Error;
use std::fmt;

/// BiLLM: Bi-directional Large Language Model Transformer Core
/// Removes causal masking to allow full context visibility during classification tasks.

#[derive(Debug)]
pub enum BiLLMError {
    DimensionMismatch,
    AllocationFailure,
}

impl fmt::Display for BiLLMError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            BiLLMError::DimensionMismatch => write!(f, "Tensor dimensions do not match for attention."),
            BiLLMError::AllocationFailure => write!(f, "Failed to allocate memory for attention matrix."),
        }
    }
}
impl Error for BiLLMError {}

pub struct SelfAttentionBlock {
    pub hidden_dim: usize,
    pub seq_length: usize,
    pub num_heads: usize,
}

impl SelfAttentionBlock {
    pub fn new(hidden_dim: usize, seq_length: usize, num_heads: usize) -> Self {
        Self {
            hidden_dim,
            seq_length,
            num_heads,
        }
    }

    /// Computes full bi-directional attention (no causal mask)
    pub fn compute_bidirectional_attention(&self, query: &[f32], key: &[f32], value: &[f32]) -> Result<Vec<f32>, BiLLMError> {
        let dim_per_head = self.hidden_dim / self.num_heads;
        if query.len() != self.seq_length * self.hidden_dim || key.len() != self.seq_length * self.hidden_dim {
            return Err(BiLLMError::DimensionMismatch);
        }

        let mut output = vec![0.0; self.seq_length * self.hidden_dim];
        let scale = 1.0 / (dim_per_head as f32).sqrt();

        for h in 0..self.num_heads {
            for i in 0..self.seq_length {
                let mut attention_scores = vec![0.0; self.seq_length];
                let mut max_score = f32::NEG_INFINITY;

                for j in 0..self.seq_length {
                    let mut score = 0.0;
                    for d in 0..dim_per_head {
                        let q_idx = i * self.hidden_dim + h * dim_per_head + d;
                        let k_idx = j * self.hidden_dim + h * dim_per_head + d;
                        score += query[q_idx] * key[k_idx];
                    }
                    score *= scale;
                    attention_scores[j] = score;
                    if score > max_score {
                        max_score = score;
                    }
                }

                // Softmax
                let mut sum_exp = 0.0;
                for j in 0..self.seq_length {
                    attention_scores[j] = (attention_scores[j] - max_score).exp();
                    sum_exp += attention_scores[j];
                }

                for j in 0..self.seq_length {
                    attention_scores[j] /= sum_exp;
                    for d in 0..dim_per_head {
                        let v_idx = j * self.hidden_dim + h * dim_per_head + d;
                        let out_idx = i * self.hidden_dim + h * dim_per_head + d;
                        output[out_idx] += attention_scores[j] * value[v_idx];
                    }
                }
            }
        }
        Ok(output)
    }
}
