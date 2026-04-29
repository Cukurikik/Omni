// Omni DAEDAL Noise Scheduler (Rust)
// System Layer: Memory-safe variable-length noise schedule computation.
// Ref: Li-Jinsong/DAEDAL — ICLR 2026

pub struct NoiseSchedule {
    pub betas: Vec<f64>,
    pub alphas_cumprod: Vec<f64>,
}

pub fn build_noise_schedule(timesteps: usize, beta_start: f64, beta_end: f64) -> Result<NoiseSchedule, &'static str> {
    if timesteps == 0 { return Err("Timesteps must be > 0"); }
    let mut betas = Vec::with_capacity(timesteps);
    let mut alphas_cumprod = Vec::with_capacity(timesteps);
    let mut cum = 1.0_f64;
    for t in 0..timesteps {
        let beta = beta_start + (beta_end - beta_start) * (t as f64 / (timesteps - 1).max(1) as f64);
        betas.push(beta);
        cum *= 1.0 - beta;
        alphas_cumprod.push(cum);
    }
    Ok(NoiseSchedule { betas, alphas_cumprod })
}

pub fn interpolate_length(src: &[f64], target_len: usize) -> Vec<f64> {
    if src.is_empty() || target_len == 0 { return vec![]; }
    let ratio = src.len() as f64 / target_len as f64;
    (0..target_len).map(|i| {
        let idx = (i as f64 * ratio).min((src.len() - 1) as f64) as usize;
        src[idx]
    }).collect()
}
