const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Model Merging Engine (SLERP / TIES / DARE)
/// Mathematically evaluates model merging techniques that combine weights from
/// multiple fine-tuned models without additional training, producing a merged
/// model that inherits capabilities from all contributors.
/// Absorbed from: Yadav et al. 2023 "TIES-Merging", Yu et al. 2023 "DARE"

pub const MergeError = error{
    DimensionMismatch,
    InvalidWeightCount,
    InvalidInterpolation,
    EmptyModels,
    NumericalInstability,
};

pub const MergeMethod = enum {
    /// Linear interpolation: W = Σ α_i · W_i
    linear,
    /// SLERP: Spherical linear interpolation on weight hypersphere
    slerp,
    /// TIES: Trim, Elect Sign, Disjoint merge
    ties,
    /// DARE: Drop And REscale before merging
    dare,
    /// Task Arithmetic: W = W_base + Σ α_i · (W_i - W_base)
    task_arithmetic,
};

pub const MergeConfig = struct {
    method: MergeMethod = .linear,
    /// Interpolation factor for 2-model merge (0.0 = model A, 1.0 = model B)
    t: f64 = 0.5,
    /// TIES trim percentage (fraction of smallest-magnitude deltas to zero out)
    ties_trim_ratio: f64 = 0.2,
    /// DARE drop rate (fraction of deltas to randomly drop)
    dare_drop_rate: f64 = 0.1,
    /// Seed for DARE random dropping
    seed: u64 = 42,
};

pub const MergeEngine = struct {
    config: MergeConfig,
    rng_state: u64,

    pub fn init(config: MergeConfig) MergeError!MergeEngine {
        if (config.t < 0.0 or config.t > 1.0) return MergeError.InvalidInterpolation;
        if (config.ties_trim_ratio < 0.0 or config.ties_trim_ratio > 1.0) return MergeError.InvalidInterpolation;
        if (config.dare_drop_rate < 0.0 or config.dare_drop_rate >= 1.0) return MergeError.InvalidInterpolation;

        return MergeEngine{
            .config = config,
            .rng_state = config.seed,
        };
    }

    fn next_random(self: *MergeEngine) f64 {
        var x = self.rng_state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.rng_state = x;
        return @as(f64, @floatFromInt(x & 0x7FFFFFFFFFFFFFFF)) /
            @as(f64, @floatFromInt(@as(u64, 0x7FFFFFFFFFFFFFFF)));
    }

    /// Linear interpolation: W = (1-t) · A + t · B
    pub fn merge_linear(a: []const f64, b: []const f64, t: f64, out: []f64) MergeError!void {
        if (a.len != b.len or a.len != out.len) return MergeError.DimensionMismatch;

        for (0..a.len) |i| {
            out[i] = (1.0 - t) * a[i] + t * b[i];
        }
    }

    /// SLERP: Spherical Linear Interpolation.
    ///
    /// Treats weight vectors as points on a hypersphere and interpolates
    /// along the great circle connecting them.
    ///
    /// SLERP(A, B, t) = sin((1-t)Ω)/sin(Ω) · A + sin(tΩ)/sin(Ω) · B
    /// Where Ω = arccos(A·B / (||A||·||B||))
    ///
    /// Advantage over linear: preserves the norm of the weight vectors,
    /// which matters because neural network layers are sensitive to scale.
    pub fn merge_slerp(a: []const f64, b: []const f64, t: f64, out: []f64) MergeError!void {
        if (a.len != b.len or a.len != out.len) return MergeError.DimensionMismatch;

        // Compute norms
        var norm_a: f64 = 0.0;
        var norm_b: f64 = 0.0;
        var dot: f64 = 0.0;

        for (0..a.len) |i| {
            norm_a += a[i] * a[i];
            norm_b += b[i] * b[i];
            dot += a[i] * b[i];
        }

        norm_a = @sqrt(norm_a);
        norm_b = @sqrt(norm_b);

        if (norm_a < 1e-10 or norm_b < 1e-10) {
            // Degenerate: fall back to linear
            return merge_linear(a, b, t, out);
        }

        // Cosine of angle between vectors
        var cos_omega = dot / (norm_a * norm_b);
        cos_omega = @max(-1.0, @min(1.0, cos_omega)); // Clamp for numerical safety

        const omega = std.math.acos(cos_omega);

        if (@abs(omega) < 1e-6) {
            // Vectors are nearly parallel: use linear
            return merge_linear(a, b, t, out);
        }

        const sin_omega = @sin(omega);
        const coeff_a = @sin((1.0 - t) * omega) / sin_omega;
        const coeff_b = @sin(t * omega) / sin_omega;

        for (0..a.len) |i| {
            out[i] = coeff_a * a[i] + coeff_b * b[i];
        }
    }

    /// Task Arithmetic: W_merged = W_base + α · (W_finetuned - W_base)
    ///
    /// The "task vector" τ = W_finetuned - W_base captures the knowledge
    /// learned during fine-tuning. Multiple task vectors can be composed:
    ///   W = W_base + Σ α_i · τ_i
    pub fn merge_task_arithmetic(
        base: []const f64,
        finetuned: []const f64,
        alpha: f64,
        out: []f64,
    ) MergeError!void {
        if (base.len != finetuned.len or base.len != out.len) return MergeError.DimensionMismatch;

        for (0..base.len) |i| {
            const task_vector = finetuned[i] - base[i];
            out[i] = base[i] + alpha * task_vector;
        }
    }

    /// TIES-Merging: Trim, Elect Sign, Disjoint merge.
    ///
    /// 1. TRIM: Zero out the smallest `trim_ratio` fraction of task vector elements
    /// 2. ELECT SIGN: For each parameter, choose the sign that the majority of
    ///    models agree on (resolves sign conflicts)
    /// 3. DISJOINT MERGE: Average only the values that agree with the elected sign
    pub fn merge_ties(
        self: *MergeEngine,
        base: []const f64,
        models: []const []const f64,
        out: []f64,
    ) MergeError!void {
        if (models.len == 0) return MergeError.EmptyModels;

        const dim = base.len;
        for (models) |m| {
            if (m.len != dim) return MergeError.DimensionMismatch;
        }
        if (out.len != dim) return MergeError.DimensionMismatch;

        const n_models = models.len;

        // For each parameter position
        for (0..dim) |i| {
            // Compute task vectors
            var positive_sum: f64 = 0.0;
            var negative_sum: f64 = 0.0;
            var positive_count: u32 = 0;
            var negative_count: u32 = 0;

            for (models) |m| {
                const delta = m[i] - base[i];

                // TRIM: skip small deltas (simplified: check absolute magnitude)
                if (@abs(delta) < self.config.ties_trim_ratio) {
                    continue;
                }

                if (delta > 0) {
                    positive_sum += delta;
                    positive_count += 1;
                } else if (delta < 0) {
                    negative_sum += delta;
                    negative_count += 1;
                }
            }

            // ELECT SIGN: majority vote
            var merged_delta: f64 = 0.0;
            if (positive_count > negative_count) {
                // Average positive contributions
                if (positive_count > 0) {
                    merged_delta = positive_sum / @as(f64, @floatFromInt(positive_count));
                }
            } else if (negative_count > 0) {
                merged_delta = negative_sum / @as(f64, @floatFromInt(negative_count));
            }

            out[i] = base[i] + merged_delta;
        }
    }

    /// DARE: Drop And REscale.
    ///
    /// Randomly drops a fraction of task vector elements, then rescales
    /// the remaining elements to compensate (unbiased estimator).
    ///
    /// For each element:
    ///   With probability p: set to 0
    ///   With probability 1-p: scale by 1/(1-p)
    ///
    /// This sparsifies the task vector, reducing interference between
    /// merged models while preserving the expected value.
    pub fn merge_dare(
        self: *MergeEngine,
        base: []const f64,
        finetuned: []const f64,
        alpha: f64,
        out: []f64,
    ) MergeError!void {
        if (base.len != finetuned.len or base.len != out.len) return MergeError.DimensionMismatch;

        const drop_rate = self.config.dare_drop_rate;
        const rescale = 1.0 / (1.0 - drop_rate);

        for (0..base.len) |i| {
            const task_vector = finetuned[i] - base[i];

            // Random drop
            if (self.next_random() < drop_rate) {
                out[i] = base[i]; // Drop: no change from base
            } else {
                out[i] = base[i] + alpha * task_vector * rescale;
            }
        }
    }
};
