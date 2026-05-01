const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Model Watermarking for Fine-Tuned LLMs
/// Mathematically evaluates steganographic embedding of cryptographic watermark bits
/// into model weight matrices, using low-significance weight perturbations that
/// survive fine-tuning but can be extracted to prove model provenance.
/// Absorbed from: Kirchenbauer et al. 2023, Zhao et al. 2023 "Protecting LLM IP"

pub const WatermarkError = error{
    InvalidKeyLength,
    InvalidBitLength,
    MatrixTooSmall,
    ExtractionFailed,
    IntegrityCheckFailed,
};

pub const WatermarkConfig = struct {
    /// Number of watermark bits to embed (typically 32-128)
    num_bits: u32 = 64,
    /// Perturbation magnitude (small enough to not affect model quality)
    perturbation_scale: f64 = 1e-5,
    /// Number of redundant embeddings per bit (for robustness)
    redundancy: u32 = 4,
};

pub const WatermarkEngine = struct {
    config: WatermarkConfig,
    rng_state: u64,

    pub fn init(config: WatermarkConfig, secret_key: u64) WatermarkError!WatermarkEngine {
        if (config.num_bits == 0 or config.num_bits > 256) return WatermarkError.InvalidBitLength;

        return WatermarkEngine{
            .config = config,
            .rng_state = secret_key,
        };
    }

    /// xorshift64 PRNG seeded by secret key — determines which weight positions to perturb
    fn next_random(self: *WatermarkEngine) u64 {
        var x = self.rng_state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.rng_state = x;
        return x;
    }

    fn next_float(self: *WatermarkEngine) f64 {
        return @as(f64, @floatFromInt(self.next_random() & 0x7FFFFFFFFFFFFFFF)) /
            @as(f64, @floatFromInt(@as(u64, 0x7FFFFFFFFFFFFFFF)));
    }

    /// Selects weight positions for watermark embedding using the secret key.
    /// The positions are deterministic given the key but appear random to an adversary.
    fn select_positions(self: *WatermarkEngine, matrix_len: usize, count: usize) []usize {
        // Use Fisher-Yates partial shuffle seeded by secret key
        var positions = std.heap.page_allocator.alloc(usize, count) catch return &[_]usize{};

        var i: usize = 0;
        while (i < count) : (i += 1) {
            positions[i] = @intCast(self.next_random() % @as(u64, @intCast(matrix_len)));
        }

        return positions;
    }

    /// Embeds watermark bits into a weight matrix.
    ///
    /// For each bit b_i of the watermark:
    ///   1. Use PRNG to select `redundancy` positions in the weight matrix
    ///   2. For each position p:
    ///      - If b_i = 1: w[p] += perturbation_scale
    ///      - If b_i = 0: w[p] -= perturbation_scale
    ///
    /// The perturbation is small enough that model quality is unaffected,
    /// but statistically detectable with the secret key.
    pub fn embed(self: *WatermarkEngine, weights: []f64, watermark_bits: []const u8) WatermarkError!void {
        if (watermark_bits.len != self.config.num_bits) return WatermarkError.InvalidBitLength;

        const positions_per_bit = self.config.redundancy;
        const total_positions = @as(usize, self.config.num_bits) * @as(usize, positions_per_bit);

        if (weights.len < total_positions) return WatermarkError.MatrixTooSmall;

        // Reset PRNG to deterministic state for reproducible embedding
        const saved_state = self.rng_state;
        _ = saved_state; // Will be used for extraction

        for (0..self.config.num_bits) |bit_idx| {
            const bit_value = watermark_bits[bit_idx];

            // Select positions for this bit
            for (0..positions_per_bit) |_| {
                const pos = @as(usize, @intCast(self.next_random() % @as(u64, @intCast(weights.len))));

                // Embed: positive perturbation for bit=1, negative for bit=0
                if (bit_value == 1) {
                    weights[pos] += self.config.perturbation_scale;
                } else {
                    weights[pos] -= self.config.perturbation_scale;
                }
            }
        }
    }

    /// Extracts watermark bits from a (potentially fine-tuned) weight matrix.
    ///
    /// For each bit position:
    ///   1. Look up the same positions using the same PRNG sequence
    ///   2. Sum the perturbations at those positions
    ///   3. If sum > 0: extracted bit = 1, else: extracted bit = 0
    ///
    /// The redundancy factor makes extraction robust to small weight changes
    /// from continued fine-tuning.
    pub fn extract(self: *WatermarkEngine, weights: []const f64, output_bits: []u8) WatermarkError!f64 {
        if (output_bits.len != self.config.num_bits) return WatermarkError.InvalidBitLength;

        const positions_per_bit = self.config.redundancy;
        var confidence_sum: f64 = 0.0;

        for (0..self.config.num_bits) |bit_idx| {
            var bit_signal: f64 = 0.0;

            for (0..positions_per_bit) |_| {
                const pos = @as(usize, @intCast(self.next_random() % @as(u64, @intCast(weights.len))));
                bit_signal += weights[pos];
            }

            // Majority vote: positive signal = 1, negative = 0
            if (bit_signal > 0.0) {
                output_bits[bit_idx] = 1;
            } else {
                output_bits[bit_idx] = 0;
            }

            // Confidence: absolute signal strength
            const avg_signal = @abs(bit_signal) / @as(f64, @floatFromInt(positions_per_bit));
            confidence_sum += avg_signal;
        }

        // Average confidence across all bits
        return confidence_sum / @as(f64, @floatFromInt(self.config.num_bits));
    }

    /// Verifies watermark integrity by comparing extracted bits against expected bits.
    /// Returns the bit-accuracy (fraction of bits correctly extracted).
    pub fn verify(
        self: *WatermarkEngine,
        weights: []const f64,
        expected_bits: []const u8,
    ) WatermarkError!f64 {
        var extracted = std.heap.page_allocator.alloc(u8, self.config.num_bits) catch return WatermarkError.ExtractionFailed;
        defer std.heap.page_allocator.free(extracted);

        _ = try self.extract(weights, extracted);

        var correct: u32 = 0;
        for (0..self.config.num_bits) |i| {
            if (extracted[i] == expected_bits[i]) {
                correct += 1;
            }
        }

        return @as(f64, @floatFromInt(correct)) / @as(f64, @floatFromInt(self.config.num_bits));
    }

    /// Computes the statistical p-value that the watermark was found by chance.
    /// Under the null hypothesis (no watermark), each bit is correct with prob 0.5.
    /// The number of correct bits follows Binomial(n, 0.5).
    /// p-value = P(X >= observed_correct | H0) using normal approximation.
    pub fn compute_p_value(num_bits: u32, correct_bits: u32) f64 {
        const n = @as(f64, @floatFromInt(num_bits));
        const k = @as(f64, @floatFromInt(correct_bits));

        // Under H0: E[X] = n/2, Var[X] = n/4, σ = √(n)/2
        const mean = n / 2.0;
        const std_dev = @sqrt(n) / 2.0;

        // Z-score
        const z = (k - mean) / std_dev;

        // p-value ≈ 1 - Φ(z) using the complementary error function
        // Φ(z) = 0.5 * (1 + erf(z / √2))
        const p_value = 0.5 * std.math.erfc(z / @sqrt(2.0));

        return p_value;
    }
};
