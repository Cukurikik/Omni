// Omni DAEDAL Noise (Mojo)
// Compute Layer: High-perf noise schedule for diffusion LLMs.
// Ref: Li-Jinsong/DAEDAL

fn build_schedule(timesteps: Int, beta_start: Float64, beta_end: Float64) -> DynamicVector[Float64]:
    var betas = DynamicVector[Float64]()
    if timesteps <= 0:
        return betas
    let denom = max(timesteps - 1, 1)
    for t in range(timesteps):
        let beta = beta_start + (beta_end - beta_start) * Float64(t) / Float64(denom)
        betas.append(beta)
    return betas
