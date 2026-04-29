// Omni Mini Transformer RoPE Kernel (Rust)
// Ref: FareedKhan-dev/create-million-parameter-llm-from-scratch

pub fn rotary_position_embedding(dim: usize, seq_len: usize, base: f64) -> Vec<Vec<f64>> {
    let half_dim = dim / 2;
    let inv_freq: Vec<f64> = (0..half_dim).map(|i| 1.0 / base.powf(2.0 * i as f64 / dim as f64)).collect();
    (0..seq_len).map(|pos| {
        inv_freq.iter().flat_map(|&freq| {
            let angle = pos as f64 * freq;
            vec![angle.cos(), angle.sin()]
        }).collect()
    }).collect()
}

pub fn rms_norm(x: &[f64], eps: f64) -> Vec<f64> {
    let n = x.len() as f64;
    let rms = (x.iter().map(|v| v * v).sum::<f64>() / n + eps).sqrt();
    x.iter().map(|v| v / rms).collect()
}

pub fn swiglu(x: &[f64], gate: &[f64]) -> Vec<f64> {
    x.iter().zip(gate.iter()).map(|(&xi, &gi)| {
        let silu = gi / (1.0 + (-gi).exp());
        silu * xi
    }).collect()
}
