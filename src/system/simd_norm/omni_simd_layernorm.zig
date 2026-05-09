// omni_simd_layernorm.zig — SIMD-Optimized Layer Normalization
// Inspired by: Custom SIMD kernels for OMNI inference
// Layer: System / Zig
//
// Vectorized LayerNorm implementation using Zig's SIMD
// intrinsics for high-throughput inference on CPU.

const std = @import("std");
const math = std.math;
const Vector = std.meta.Vector;

const VECTOR_SIZE = 8; // AVX2 float32 lanes
const VecF32 = @Vector(VECTOR_SIZE, f32);

/// Compute mean of a float32 slice using SIMD accumulation.
pub fn simd_mean(data: []const f32) f32 {
    const len = data.len;
    if (len == 0) return 0.0;

    const simd_len = len / VECTOR_SIZE * VECTOR_SIZE;
    var sum_vec: VecF32 = @splat(0.0);

    var i: usize = 0;
    while (i < simd_len) : (i += VECTOR_SIZE) {
        const chunk: VecF32 = data[i..][0..VECTOR_SIZE].*;
        sum_vec += chunk;
    }

    // Horizontal sum of vector lanes
    var total: f32 = @reduce(.Add, sum_vec);

    // Handle remainder
    while (i < len) : (i += 1) {
        total += data[i];
    }

    return total / @as(f32, @floatFromInt(len));
}

/// Compute variance of a float32 slice given the mean.
pub fn simd_variance(data: []const f32, mean: f32) f32 {
    const len = data.len;
    if (len == 0) return 0.0;

    const simd_len = len / VECTOR_SIZE * VECTOR_SIZE;
    const mean_vec: VecF32 = @splat(mean);
    var var_vec: VecF32 = @splat(0.0);

    var i: usize = 0;
    while (i < simd_len) : (i += VECTOR_SIZE) {
        const chunk: VecF32 = data[i..][0..VECTOR_SIZE].*;
        const diff = chunk - mean_vec;
        var_vec += diff * diff;
    }

    var variance: f32 = @reduce(.Add, var_vec);

    // Handle remainder
    while (i < len) : (i += 1) {
        const diff = data[i] - mean;
        variance += diff * diff;
    }

    return variance / @as(f32, @floatFromInt(len));
}

/// SIMD-optimized Layer Normalization in-place.
///
/// Normalizes each row of shape (batch, dim) to zero mean and unit variance,
/// then applies affine transformation: output = gamma * normalized + beta.
///
/// Parameters:
///   data: mutable slice of f32 (will be modified in-place)
///   gamma: scale parameters (length = dim)
///   beta: shift parameters (length = dim)
///   batch_size: number of rows
///   dim: feature dimension
///   eps: small constant for numerical stability
pub fn layer_norm(
    data: []f32,
    gamma: []const f32,
    beta: []const f32,
    batch_size: usize,
    dim: usize,
    eps: f32,
) void {
    std.debug.assert(data.len == batch_size * dim);
    std.debug.assert(gamma.len == dim);
    std.debug.assert(beta.len == dim);

    const simd_dim = dim / VECTOR_SIZE * VECTOR_SIZE;
    const eps_vec: VecF32 = @splat(eps);

    for (0..batch_size) |b| {
        const offset = b * dim;
        const row = data[offset .. offset + dim];

        // Compute mean
        const mean = simd_mean(row);
        const mean_vec: VecF32 = @splat(mean);

        // Compute variance
        const variance = simd_variance(row, mean);
        const inv_std = 1.0 / @sqrt(variance + eps);
        const inv_std_vec: VecF32 = @splat(inv_std);

        // Normalize and apply affine transform (SIMD)
        var i: usize = 0;
        while (i < simd_dim) : (i += VECTOR_SIZE) {
            const x: VecF32 = row[i..][0..VECTOR_SIZE].*;
            const g: VecF32 = gamma[i..][0..VECTOR_SIZE].*;
            const b_vec: VecF32 = beta[i..][0..VECTOR_SIZE].*;

            const normalized = (x - mean_vec) * inv_std_vec;
            const result = normalized * g + b_vec;

            data[offset + i ..][0..VECTOR_SIZE].* = result;
        }

        // Handle remainder
        while (i < dim) : (i += 1) {
            const normalized = (row[i] - mean) * inv_std;
            data[offset + i] = normalized * gamma[i] + beta[i];
        }
    }
}

/// RMSNorm: Root Mean Square Layer Normalization (no mean subtraction).
/// Used in Llama-style architectures.
pub fn rms_norm(
    data: []f32,
    gamma: []const f32,
    batch_size: usize,
    dim: usize,
    eps: f32,
) void {
    std.debug.assert(data.len == batch_size * dim);
    std.debug.assert(gamma.len == dim);

    const simd_dim = dim / VECTOR_SIZE * VECTOR_SIZE;

    for (0..batch_size) |b| {
        const offset = b * dim;
        const row = data[offset .. offset + dim];

        // Compute RMS
        var sum_sq: f32 = 0.0;
        var sq_vec: VecF32 = @splat(0.0);

        var i: usize = 0;
        while (i < simd_dim) : (i += VECTOR_SIZE) {
            const x: VecF32 = row[i..][0..VECTOR_SIZE].*;
            sq_vec += x * x;
        }
        sum_sq = @reduce(.Add, sq_vec);

        while (i < dim) : (i += 1) {
            sum_sq += row[i] * row[i];
        }

        const rms = @sqrt(sum_sq / @as(f32, @floatFromInt(dim)) + eps);
        const inv_rms = 1.0 / rms;
        const inv_rms_vec: VecF32 = @splat(inv_rms);

        // Normalize with gamma
        i = 0;
        while (i < simd_dim) : (i += VECTOR_SIZE) {
            const x: VecF32 = row[i..][0..VECTOR_SIZE].*;
            const g: VecF32 = gamma[i..][0..VECTOR_SIZE].*;
            const result = x * inv_rms_vec * g;
            data[offset + i ..][0..VECTOR_SIZE].* = result;
        }

        while (i < dim) : (i += 1) {
            data[offset + i] = row[i] * inv_rms * gamma[i];
        }
    }
}

/// Benchmark helper: time a LayerNorm call.
pub fn benchmark_layer_norm(batch: usize, dim: usize, iterations: usize) f64 {
    var arena = std.heap.page_allocator;
    const data = arena.alloc(f32, batch * dim) catch return -1;
    defer arena.free(data);
    const gamma = arena.alloc(f32, dim) catch return -1;
    defer arena.free(gamma);
    const beta = arena.alloc(f32, dim) catch return -1;
    defer arena.free(beta);

    // Initialize
    for (gamma) |*g| g.* = 1.0;
    for (beta) |*b| b.* = 0.0;
    for (data) |*d| d.* = 0.5;

    const timer = std.time.Timer{};
    const start = timer.read();

    for (0..iterations) |_| {
        layer_norm(data, gamma, beta, batch, dim, 1e-5);
    }

    const elapsed = timer.read() - start;
    return @as(f64, @floatFromInt(elapsed)) / @as(f64, @floatFromInt(iterations));
}

test "simd_mean basic" {
    const data = [_]f32{ 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0 };
    const mean = simd_mean(&data);
    try std.testing.expectApproxEqAbs(mean, 5.5, 1e-5);
}

test "layer_norm identity" {
    var data = [_]f32{ 1.0, 2.0, 3.0, 4.0 };
    const gamma = [_]f32{ 1.0, 1.0, 1.0, 1.0 };
    const beta = [_]f32{ 0.0, 0.0, 0.0, 0.0 };

    layer_norm(&data, &gamma, &beta, 1, 4, 1e-5);

    // Mean should be ~0 after normalization
    const new_mean = simd_mean(&data);
    try std.testing.expectApproxEqAbs(new_mean, 0.0, 1e-5);
}
