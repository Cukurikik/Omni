// OMNI System — Zig Comptime Transformer Kernel
// Compile-time optimized attention computation.

const std = @import("std");
const math = std.math;

pub fn ComptimeTransformer(comptime dim: usize, comptime heads: usize) type {
    const head_dim = dim / heads;
    const scale: f32 = 1.0 / @sqrt(@as(f32, @floatFromInt(head_dim)));

    return struct {
        const Self = @This();

        pub fn rmsnorm(out: *[dim]f32, x: *const [dim]f32, weight: *const [dim]f32) void {
            var ss: f32 = 0.0;
            inline for (0..dim) |i| { ss += x[i] * x[i]; }
            ss = 1.0 / @sqrt(ss / @as(f32, @floatFromInt(dim)) + 1e-5);
            inline for (0..dim) |i| { out[i] = weight[i] * (x[i] * ss); }
        }

        pub fn softmax(x: []f32) void {
            var max_val: f32 = -math.inf(f32);
            for (x) |v| { if (v > max_val) max_val = v; }
            var sum: f32 = 0.0;
            for (x) |*v| { v.* = @exp(v.* - max_val); sum += v.*; }
            const inv = 1.0 / sum;
            for (x) |*v| { v.* *= inv; }
        }

        pub fn silu(x: []f32) void {
            for (x) |*v| { v.* = v.* / (1.0 + @exp(-v.*)); }
        }

        pub fn matmul(out: []f32, a: []const f32, b: []const f32, M: usize, K: usize, N: usize) void {
            @memset(out, 0);
            for (0..M) |i| {
                for (0..K) |k| {
                    const a_val = a[i * K + k];
                    for (0..N) |j| {
                        out[i * N + j] += a_val * b[k * N + j];
                    }
                }
            }
        }

        pub fn attention_single_head(
            output: *[head_dim]f32,
            query: *const [head_dim]f32,
            key_cache: []const f32,
            value_cache: []const f32,
            pos: usize,
        ) void {
            var scores: [2048]f32 = undefined;
            for (0..pos + 1) |t| {
                var s: f32 = 0.0;
                for (0..head_dim) |i| {
                    s += query[i] * key_cache[t * head_dim + i];
                }
                scores[t] = s * scale;
            }
            softmax(scores[0..pos + 1]);
            @memset(output, 0);
            for (0..pos + 1) |t| {
                for (0..head_dim) |i| {
                    output[i] += scores[t] * value_cache[t * head_dim + i];
                }
            }
        }

        pub fn gelu(x: []f32) void {
            for (x) |*v| {
                const val = v.*;
                v.* = 0.5 * val * (1.0 + @tanh(0.7978845608 * (val + 0.044715 * val * val * val)));
            }
        }
    };
}

pub const Transformer256x8 = ComptimeTransformer(256, 8);
pub const Transformer512x8 = ComptimeTransformer(512, 8);
pub const Transformer768x12 = ComptimeTransformer(768, 12);
pub const Transformer1024x16 = ComptimeTransformer(1024, 16);
