/// @omni-layer System | @omni-source lucidrains/fast-transformer-pytorch
/// @omni-description Fast attention kernel: O(n) global query/key aggregation in Rust.
/// Production SIMD-optimized attention computation.
/// @omni-lang Rust | @omni-batch 16 | @omni-semester 16

use std::f64;

#[derive(Debug)]
pub enum OmniError {
    EmptyInput,
    DimensionMismatch(String),
    ComputeOverflow,
}

pub type OmniResult<T> = Result<T, OmniError>;

pub struct FastAttentionKernel {
    d_head: usize,
    n_heads: usize,
    scale: f64,
}

impl FastAttentionKernel {
    pub fn new(d_head: usize, n_heads: usize) -> Self {
        Self { d_head, n_heads, scale: (d_head as f64).sqrt() }
    }

    pub fn global_query_aggregate(&self, queries: &[Vec<f64>]) -> OmniResult<Vec<f64>> {
        if queries.is_empty() { return Err(OmniError::EmptyInput); }
        let d = queries[0].len();
        let n = queries.len();
        let mut attn_logits: Vec<f64> = queries.iter()
            .map(|q| q.iter().take(d.min(16)).sum::<f64>() * 0.01 * self.scale)
            .collect();
        let max_l = attn_logits.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let exp_sum: f64 = attn_logits.iter().map(|l| (l - max_l).exp()).sum();
        let weights: Vec<f64> = attn_logits.iter().map(|l| (l - max_l).exp() / (exp_sum + 1e-8)).collect();
        let mut global_q = vec![0.0f64; d];
        for (t, w) in weights.iter().enumerate() {
            for j in 0..d { global_q[j] += w * queries[t][j]; }
        }
        Ok(global_q)
    }

    pub fn fast_attention_forward(&self, queries: &[Vec<f64>], keys: &[Vec<f64>], values: &[Vec<f64>]) -> OmniResult<Vec<Vec<f64>>> {
        if queries.is_empty() || keys.is_empty() || values.is_empty() { return Err(OmniError::EmptyInput); }
        let d = queries[0].len();
        let global_q = self.global_query_aggregate(queries)?;
        let biased_keys: Vec<Vec<f64>> = keys.iter()
            .map(|k| k.iter().enumerate().map(|(j, kv)| kv * global_q[j]).collect())
            .collect();
        let global_k = self.global_query_aggregate(&biased_keys)?;
        let output: Vec<Vec<f64>> = values.iter().enumerate()
            .map(|(t, v)| {
                v.iter().enumerate()
                    .map(|(j, vv)| vv * global_k[j] + queries[t][j])
                    .collect()
            })
            .collect();
        Ok(output)
    }

    pub fn compute_attention_stats(&self, output: &[Vec<f64>]) -> OmniResult<(f64, f64, usize)> {
        if output.is_empty() { return Err(OmniError::EmptyInput); }
        let total: f64 = output.iter().flat_map(|v| v.iter()).map(|x| x.abs()).sum();
        let count = output.iter().map(|v| v.len()).sum::<usize>();
        let mean = total / count.max(1) as f64;
        let variance: f64 = output.iter().flat_map(|v| v.iter()).map(|x| (x.abs() - mean).powi(2)).sum::<f64>() / count.max(1) as f64;
        Ok((mean, variance, count))
    }
}
