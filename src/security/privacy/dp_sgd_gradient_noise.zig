const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Gradient Noise Injection for Differential Privacy
/// Mathematically evaluates calibrated Gaussian noise addition to gradient tensors,
/// bounding the privacy loss (ε, δ) via the Rényi Differential Privacy accountant.
/// This prevents the fine-tuned model from memorizing individual training examples.
/// Absorbed from: Abadi et al. 2016 "Deep Learning with Differential Privacy", DP-SGD

pub const DPError = error{
    InvalidEpsilon,
    InvalidDelta,
    InvalidClipNorm,
    InvalidNoiseMultiplier,
    GradientDimensionMismatch,
};

pub const DPConfig = struct {
    /// Maximum L2 norm for per-sample gradient clipping
    max_grad_norm: f64 = 1.0,
    /// Noise multiplier σ: higher = more privacy, less utility
    noise_multiplier: f64 = 1.0,
    /// Target privacy budget ε
    target_epsilon: f64 = 8.0,
    /// Failure probability δ (typically 1/N where N = dataset size)
    target_delta: f64 = 1e-5,
    /// Sampling rate q = batch_size / dataset_size
    sampling_rate: f64 = 0.01,
};

pub const DPGradientEngine = struct {
    config: DPConfig,
    /// Linear Congruential Generator state for deterministic noise
    rng_state: u64,
    /// Running privacy budget tracker
    accumulated_epsilon: f64,
    steps_taken: u64,

    pub fn init(config: DPConfig, seed: u64) DPError!DPGradientEngine {
        if (config.max_grad_norm <= 0.0) return DPError.InvalidClipNorm;
        if (config.noise_multiplier <= 0.0) return DPError.InvalidNoiseMultiplier;
        if (config.target_epsilon <= 0.0) return DPError.InvalidEpsilon;
        if (config.target_delta <= 0.0 or config.target_delta >= 1.0) return DPError.InvalidDelta;

        return DPGradientEngine{
            .config = config,
            .rng_state = seed,
            .accumulated_epsilon = 0.0,
            .steps_taken = 0,
        };
    }

    /// Generates a pseudo-random float in [0, 1) using xorshift64
    fn next_uniform(self: *DPGradientEngine) f64 {
        var x = self.rng_state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.rng_state = x;
        // Map to [0, 1)
        return @as(f64, @floatFromInt(x & 0x7FFFFFFFFFFFFFFF)) / @as(f64, @floatFromInt(@as(u64, 0x7FFFFFFFFFFFFFFF)));
    }

    /// Box-Muller transform: generates standard normal N(0,1) samples
    fn next_gaussian(self: *DPGradientEngine) f64 {
        const u1 = self.next_uniform();
        const u2 = self.next_uniform();
        // Prevent log(0)
        const safe_u1 = if (u1 < 1e-15) 1e-15 else u1;
        return @sqrt(-2.0 * @log(safe_u1)) * @cos(2.0 * std.math.pi * u2);
    }

    /// Clips a single gradient vector to have L2 norm <= max_grad_norm.
    /// Returns the original norm before clipping.
    pub fn clip_gradient(self: *const DPGradientEngine, gradient: []f64) f64 {
        // Compute L2 norm
        var norm_sq: f64 = 0.0;
        for (gradient) |g| {
            norm_sq += g * g;
        }
        const norm = @sqrt(norm_sq);

        // Clip if norm exceeds threshold
        if (norm > self.config.max_grad_norm) {
            const scale = self.config.max_grad_norm / (norm + 1e-12);
            for (gradient) |*g| {
                g.* *= scale;
            }
        }

        return norm;
    }

    /// Adds calibrated Gaussian noise to the aggregated (clipped) gradient.
    /// Noise scale = max_grad_norm * noise_multiplier / batch_size
    /// Each gradient element gets independent N(0, σ²) noise.
    pub fn add_noise(self: *DPGradientEngine, gradient: []f64, batch_size: u32) void {
        const noise_std = self.config.max_grad_norm * self.config.noise_multiplier / @as(f64, @floatFromInt(batch_size));

        for (gradient) |*g| {
            const noise = self.next_gaussian() * noise_std;
            g.* += noise;
        }
    }

    /// Executes one full DP-SGD step:
    /// 1. Clip each per-sample gradient
    /// 2. Average the clipped gradients
    /// 3. Add calibrated noise
    /// 4. Update privacy accountant
    pub fn dp_sgd_step(
        self: *DPGradientEngine,
        per_sample_gradients: [][]f64,
        aggregated_output: []f64,
        param_count: usize,
    ) DPError!void {
        const batch_size = per_sample_gradients.len;
        if (batch_size == 0) return;

        // Zero the output
        for (aggregated_output) |*v| {
            v.* = 0.0;
        }

        // 1. Clip and aggregate
        for (per_sample_gradients) |sample_grad| {
            if (sample_grad.len != param_count) return DPError.GradientDimensionMismatch;

            // Clip this sample's gradient
            _ = self.clip_gradient(sample_grad);

            // Accumulate into aggregate
            for (0..param_count) |j| {
                aggregated_output[j] += sample_grad[j];
            }
        }

        // 2. Average
        const batch_f = @as(f64, @floatFromInt(batch_size));
        for (aggregated_output) |*v| {
            v.* /= batch_f;
        }

        // 3. Add noise
        self.add_noise(aggregated_output, @intCast(batch_size));

        // 4. Update privacy accountant
        self.steps_taken += 1;
        self.accumulated_epsilon = self.compute_epsilon_spent();
    }

    /// Computes the accumulated privacy budget ε using a simplified
    /// Rényi Differential Privacy (RDP) accountant.
    /// 
    /// For Gaussian mechanism with noise multiplier σ:
    ///   RDP at order α: ρ(α) = α / (2σ²)
    ///   After T compositions with subsampling rate q:
    ///   ε ≈ T · q² · α / (2σ²) + log(1/δ) / (α - 1)
    /// 
    /// We optimize over α to find the tightest bound.
    pub fn compute_epsilon_spent(self: *const DPGradientEngine) f64 {
        const T = @as(f64, @floatFromInt(self.steps_taken));
        const sigma = self.config.noise_multiplier;
        const q = self.config.sampling_rate;
        const delta = self.config.target_delta;

        var best_epsilon: f64 = std.math.inf(f64);

        // Search over RDP orders α ∈ [2, 128]
        var alpha: f64 = 2.0;
        while (alpha <= 128.0) : (alpha += 1.0) {
            // RDP guarantee per step (simplified Gaussian mechanism)
            const rdp_per_step = q * q * alpha / (2.0 * sigma * sigma);

            // Total RDP after T compositions
            const total_rdp = T * rdp_per_step;

            // Convert RDP to (ε, δ)-DP
            const epsilon = total_rdp + @log(1.0 / delta) / (alpha - 1.0);

            if (epsilon < best_epsilon) {
                best_epsilon = epsilon;
            }
        }

        return best_epsilon;
    }

    /// Returns whether the privacy budget has been exceeded
    pub fn is_budget_exhausted(self: *const DPGradientEngine) bool {
        return self.accumulated_epsilon >= self.config.target_epsilon;
    }
};
