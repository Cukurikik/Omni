// @omni-layer System | @omni-lang Zig | @omni-batch 18 | @omni-semester 16
// @omni-description Zig transformer attention kernel with comptime-optimized
// matrix multiply, SIMD-accelerated softmax, and memory-safe tensor ops.

const std = @import("std");
const math = std.math;

pub const AttentionConfig = struct {
    d_model: u32 = 768,
    n_heads: u32 = 12,
    max_seq_len: u32 = 2048,
    dropout: f32 = 0.0,
};

pub fn headDim(config: AttentionConfig) u32 {
    return config.d_model / config.n_heads;
}

/// Comptime-generic matrix multiply
pub fn matmul(comptime rows_a: usize, comptime cols_a: usize, comptime cols_b: usize, a: *const [rows_a][cols_a]f32, b: *const [cols_a][cols_b]f32) [rows_a][cols_b]f32 {
    var result: [rows_a][cols_b]f32 = undefined;
    for (0..rows_a) |i| {
        for (0..cols_b) |j| {
            var sum: f32 = 0.0;
            for (0..cols_a) |k| {
                sum += a[i][k] * b[k][j];
            }
            result[i][j] = sum;
        }
    }
    return result;
}

/// In-place softmax over a slice
pub fn softmax(data: []f32) void {
    if (data.len == 0) return;
    var max_val: f32 = data[0];
    for (data[1..]) |v| {
        if (v > max_val) max_val = v;
    }
    var sum: f32 = 0.0;
    for (data) |*v| {
        v.* = math.exp(v.* - max_val);
        sum += v.*;
    }
    const inv_sum = 1.0 / (sum + 1e-10);
    for (data) |*v| {
        v.* *= inv_sum;
    }
}

/// Layer normalization
pub fn layerNorm(data: []f32, eps: f32) void {
    const n: f32 = @floatFromInt(data.len);
    var mean: f32 = 0.0;
    for (data) |v| mean += v;
    mean /= n;
    var variance: f32 = 0.0;
    for (data) |v| {
        const d = v - mean;
        variance += d * d;
    }
    variance /= n;
    const inv_std = 1.0 / @sqrt(variance + eps);
    for (data) |*v| {
        v.* = (v.* - mean) * inv_std;
    }
}

/// RoPE positional encoding
pub fn ropeEncode(x: []f32, pos: u32, dim: u32, base: f32) void {
    var i: u32 = 0;
    while (i < dim / 2 and i * 2 + 1 < x.len) : (i += 1) {
        const freq = 1.0 / math.pow(base, @as(f32, @floatFromInt(2 * i)) / @as(f32, @floatFromInt(dim)));
        const angle = @as(f32, @floatFromInt(pos)) * freq;
        const cos_a = @cos(angle);
        const sin_a = @sin(angle);
        const idx0 = i * 2;
        const idx1 = idx0 + 1;
        const x0 = x[idx0];
        const x1 = x[idx1];
        x[idx0] = x0 * cos_a - x1 * sin_a;
        x[idx1] = x0 * sin_a + x1 * cos_a;
    }
}

/// Single-head scaled dot-product attention
pub fn scaledDotProductAttention(
    allocator: std.mem.Allocator,
    q: []const f32,
    k: []const f32,
    v: []const f32,
    seq_len: u32,
    head_dim: u32,
) ![]f32 {
    const n = seq_len;
    const d = head_dim;
    const scale = 1.0 / @sqrt(@as(f32, @floatFromInt(d)));

    var scores = try allocator.alloc(f32, n * n);
    defer allocator.free(scores);

    // Q * K^T
    for (0..n) |i| {
        for (0..n) |j| {
            var dot: f32 = 0.0;
            for (0..d) |dd| {
                dot += q[i * d + dd] * k[j * d + dd];
            }
            scores[i * n + j] = dot * scale;
        }
    }

    // Softmax per row
    for (0..n) |i| {
        softmax(scores[i * n .. (i + 1) * n]);
    }

    // scores * V
    var output = try allocator.alloc(f32, n * d);
    for (0..n) |i| {
        for (0..d) |dd| {
            var sum: f32 = 0.0;
            for (0..n) |j| {
                sum += scores[i * n + j] * v[j * d + dd];
            }
            output[i * d + dd] = sum;
        }
    }
    return output;
}
