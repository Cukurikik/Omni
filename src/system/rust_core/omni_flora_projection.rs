// Omni Flora Random Projection Kernel (Rust)
// Ref: BorealisAI/flora-opt — ICML 2024
pub fn random_hash(seed: u64, idx: u64) -> u64 {
    seed.wrapping_mul(idx.wrapping_add(1)).wrapping_mul(2654435761) >> 16
}
pub fn compress(gradient: &[f64], proj_dim: usize, seed: u64) -> Vec<f64> {
    let mut compressed = vec![0.0f64; proj_dim];
    let scale = 1.0 / (proj_dim as f64).sqrt();
    for (i, &g) in gradient.iter().enumerate() {
        let h = (random_hash(seed, i as u64) as usize) % proj_dim;
        let sign = if (random_hash(seed.wrapping_add(1), i as u64) % 2) == 0 { 1.0 } else { -1.0 };
        compressed[h] += g * sign * scale;
    }
    compressed
}
pub fn flora_step(params: &mut [f64], gradient: &[f64], lr: f64, proj_dim: usize, seed: u64) {
    let c = compress(gradient, proj_dim, seed);
    for (i, p) in params.iter_mut().enumerate() {
        let h = (random_hash(seed, i as u64) as usize) % proj_dim;
        let sign = if (random_hash(seed.wrapping_add(1), i as u64) % 2) == 0 { 1.0 } else { -1.0 };
        *p -= lr * c[h] * sign * (proj_dim as f64).sqrt();
    }
}
