// OMNI System Layer — Zig Comptime Transformer Kernel
// Zero-overhead transformer attention using Zig comptime metaprogramming.

const std = @import("std");
const math = std.math;
const mem = std.mem;
const Allocator = std.mem.Allocator;

/// Transformer configuration resolved at compile time
pub fn TransformerConfig(comptime embed_dim: usize, comptime num_heads: usize, comptime max_seq: usize) type {
    return struct {
        pub const EMBED_DIM = embed_dim;
        pub const NUM_HEADS = num_heads;
        pub const HEAD_DIM = embed_dim / num_heads;
        pub const MAX_SEQ_LEN = max_seq;
        pub const SCALE: f32 = 1.0 / @sqrt(@as(f32, @floatFromInt(embed_dim / num_heads)));

        const Self = @This();

        /// Attention state for one layer
        pub const AttentionState = struct {
            key_cache: [max_seq][embed_dim]f32,
            value_cache: [max_seq][embed_dim]f32,
            seq_len: usize,

            pub fn init() AttentionState {
                return .{
                    .key_cache = mem.zeroes([max_seq][embed_dim]f32),
                    .value_cache = mem.zeroes([max_seq][embed_dim]f32),
                    .seq_len = 0,
                };
            }

            pub fn append(self: *AttentionState, key: [embed_dim]f32, value: [embed_dim]f32) void {
                if (self.seq_len < max_seq) {
                    self.key_cache[self.seq_len] = key;
                    self.value_cache[self.seq_len] = value;
                    self.seq_len += 1;
                }
            }

            pub fn clear(self: *AttentionState) void {
                self.seq_len = 0;
            }
        };

        /// Compute single-head attention score
        pub fn dotProduct(a: []const f32, b: []const f32) f32 {
            var sum: f32 = 0.0;
            const len = @min(a.len, b.len);
            var i: usize = 0;
            // SIMD-friendly loop
            while (i + 4 <= len) : (i += 4) {
                sum += a[i] * b[i] + a[i + 1] * b[i + 1] + a[i + 2] * b[i + 2] + a[i + 3] * b[i + 3];
            }
            while (i < len) : (i += 1) {
                sum += a[i] * b[i];
            }
            return sum;
        }

        /// Softmax in-place
        pub fn softmax(data: []f32) void {
            var max_val: f32 = -math.inf(f32);
            for (data) |v| {
                if (v > max_val) max_val = v;
            }
            var sum: f32 = 0.0;
            for (data) |*v| {
                v.* = @exp(v.* - max_val);
                sum += v.*;
            }
            const inv = 1.0 / sum;
            for (data) |*v| {
                v.* *= inv;
            }
        }

        /// RMS Normalization
        pub fn rmsNorm(out: []f32, x: []const f32, weight: []const f32, eps: f32) void {
            var ss: f32 = 0.0;
            for (x) |v| {
                ss += v * v;
            }
            ss = 1.0 / @sqrt(ss / @as(f32, @floatFromInt(x.len)) + eps);
            for (out, x, weight) |*o, xi, wi| {
                o.* = xi * ss * wi;
            }
        }

        /// SiLU activation (used in LLaMA FFN)
        pub fn silu(x: []f32) void {
            for (x) |*v| {
                v.* = v.* / (1.0 + @exp(-v.*));
            }
        }

        /// GELU activation
        pub fn gelu(x: []f32) void {
            const sqrt_2_pi: f32 = 0.7978845608;
            const coeff: f32 = 0.044715;
            for (x) |*v| {
                const t = sqrt_2_pi * (v.* + coeff * v.* * v.* * v.*);
                v.* = 0.5 * v.* * (1.0 + math.tanh(t));
            }
        }

        /// Matrix-vector multiply: out = mat @ vec
        pub fn matvec(out: []f32, mat: []const f32, vec: []const f32, rows: usize, cols: usize) void {
            for (0..rows) |r| {
                var sum: f32 = 0.0;
                const row_start = r * cols;
                for (0..cols) |c| {
                    sum += mat[row_start + c] * vec[c];
                }
                out[r] = sum;
            }
        }
    };
}

/// Production Zig transformer config for 7B-class model
pub const Omni7BConfig = TransformerConfig(4096, 32, 8192);

/// Smaller config for testing and edge deployment
pub const OmniTinyConfig = TransformerConfig(256, 4, 2048);

test "dot product" {
    const Config = TransformerConfig(64, 4, 128);
    const a = [_]f32{ 1.0, 2.0, 3.0, 4.0 };
    const b = [_]f32{ 4.0, 3.0, 2.0, 1.0 };
    const result = Config.dotProduct(&a, &b);
    try std.testing.expectApproxEqAbs(@as(f32, 20.0), result, 0.001);
}

test "softmax" {
    const Config = TransformerConfig(64, 4, 128);
    var data = [_]f32{ 1.0, 2.0, 3.0 };
    Config.softmax(&data);
    var sum: f32 = 0.0;
    for (data) |v| sum += v;
    try std.testing.expectApproxEqAbs(@as(f32, 1.0), sum, 0.001);
}
