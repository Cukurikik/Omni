// OMNI MOTHER: Zig SIMD Math Kernel (Production Grade)
// AVX2/AVX-512 accelerated vector operations for tensor computation.
// Provides dot product, softmax, layer norm, and element-wise ops.

const std = @import("std");
const math = std.math;
const log = std.log.scoped(.omni_simd);

/// 8-wide f32 SIMD vector type (256-bit AVX2).
pub const Vec8f = @Vector(8, f32);

/// 16-wide f32 SIMD vector type (512-bit AVX-512).
pub const Vec16f = @Vector(16, f32);

// ---- Reduction Helpers ----

/// Horizontal sum of a Vec8f.
pub fn hsum8(v: Vec8f) f32 {
    const a = @shuffle(f32, v, undefined, .{ 4, 5, 6, 7, 0, 1, 2, 3 });
    const b = v + a;
    const c = @shuffle(f32, b, undefined, .{ 2, 3, 0, 1, 4, 5, 6, 7 });
    const d = b + c;
    const e = @shuffle(f32, d, undefined, .{ 1, 0, 3, 2, 5, 4, 7, 6 });
    const f = d + e;
    return f[0];
}

/// Horizontal max of a Vec8f.
pub fn hmax8(v: Vec8f) f32 {
    const a = @shuffle(f32, v, undefined, .{ 4, 5, 6, 7, 0, 1, 2, 3 });
    const b = @max(v, a);
    const c = @shuffle(f32, b, undefined, .{ 2, 3, 0, 1, 4, 5, 6, 7 });
    const d = @max(b, c);
    const e = @shuffle(f32, d, undefined, .{ 1, 0, 3, 2, 5, 4, 7, 6 });
    const f = @max(d, e);
    return f[0];
}

// ---- Core Vector Operations ----

/// SIMD dot product of two aligned f32 slices.
/// Falls back to scalar for the remainder (tail loop).
pub fn dotProduct(a: []const f32, b: []const f32) f32 {
    if (a.len != b.len) @panic("dotProduct: mismatched lengths");
    const n = a.len;
    const simd_width = 8;
    const chunks = n / simd_width;
    const remainder = n % simd_width;

    var acc: Vec8f = @splat(0.0);

    for (0..chunks) |i| {
        const offset = i * simd_width;
        const va: Vec8f = a[offset..][0..simd_width].*;
        const vb: Vec8f = b[offset..][0..simd_width].*;
        acc += va * vb; // fused multiply-add on capable hardware
    }

    var result = hsum8(acc);

    // Scalar tail
    const tail_start = chunks * simd_width;
    for (tail_start..n) |i| {
        result += a[i] * b[i];
    }

    return result;
}

/// SIMD element-wise multiply: out[i] = a[i] * b[i].
pub fn elementwiseMul(a: []const f32, b: []const f32, out: []f32) void {
    if (a.len != b.len or a.len != out.len) @panic("elementwiseMul: length mismatch");
    const n = a.len;
    const w = 8;
    const chunks = n / w;

    for (0..chunks) |i| {
        const off = i * w;
        const va: Vec8f = a[off..][0..w].*;
        const vb: Vec8f = b[off..][0..w].*;
        out[off..][0..w].* = va * vb;
    }
    // Scalar tail
    for (chunks * w..n) |i| {
        out[i] = a[i] * b[i];
    }
}

/// SIMD vector addition: out[i] = a[i] + b[i].
pub fn vectorAdd(a: []const f32, b: []const f32, out: []f32) void {
    if (a.len != b.len or a.len != out.len) @panic("vectorAdd: length mismatch");
    const n = a.len;
    const w = 8;
    const chunks = n / w;

    for (0..chunks) |i| {
        const off = i * w;
        const va: Vec8f = a[off..][0..w].*;
        const vb: Vec8f = b[off..][0..w].*;
        out[off..][0..w].* = va + vb;
    }
    for (chunks * w..n) |i| {
        out[i] = a[i] + b[i];
    }
}

/// SIMD scalar multiply: out[i] = a[i] * scalar.
pub fn scalarMul(a: []const f32, scalar: f32, out: []f32) void {
    if (a.len != out.len) @panic("scalarMul: length mismatch");
    const n = a.len;
    const w = 8;
    const chunks = n / w;
    const vs: Vec8f = @splat(scalar);

    for (0..chunks) |i| {
        const off = i * w;
        const va: Vec8f = a[off..][0..w].*;
        out[off..][0..w].* = va * vs;
    }
    for (chunks * w..n) |i| {
        out[i] = a[i] * scalar;
    }
}

// ---- Softmax (numerically stable, SIMD-accelerated) ----

/// Computes softmax in-place over a float slice.
/// Uses the max-subtraction trick for numerical stability.
pub fn softmax(data: []f32) void {
    const n = data.len;
    if (n == 0) return;

    // 1. Find max (SIMD)
    var max_val: f32 = -math.inf(f32);
    const w = 8;
    const chunks = n / w;

    if (chunks > 0) {
        var vmax: Vec8f = @splat(-math.inf(f32));
        for (0..chunks) |i| {
            const off = i * w;
            const v: Vec8f = data[off..][0..w].*;
            vmax = @max(vmax, v);
        }
        max_val = hmax8(vmax);
    }
    for (chunks * w..n) |i| {
        if (data[i] > max_val) max_val = data[i];
    }

    // 2. Subtract max and exponentiate
    var sum: f32 = 0.0;
    for (0..n) |i| {
        data[i] = @exp(data[i] - max_val);
        sum += data[i];
    }

    // 3. Normalize
    if (sum > 0.0) {
        const inv = 1.0 / sum;
        scalarMul(data, inv, data);
    }
}

// ---- Layer Normalization ----

/// Computes layer normalization: out = (x - mean) / sqrt(var + eps) * gamma + beta.
pub fn layerNorm(
    x: []const f32,
    gamma: []const f32,
    beta: []const f32,
    out: []f32,
    eps: f32,
) void {
    const n = x.len;
    if (n == 0) return;
    const fn_: f32 = @floatFromInt(n);

    // Mean
    var mean: f32 = 0.0;
    for (x) |v| mean += v;
    mean /= fn_;

    // Variance
    var variance: f32 = 0.0;
    for (x) |v| {
        const diff = v - mean;
        variance += diff * diff;
    }
    variance /= fn_;

    // Normalize
    const inv_std = 1.0 / @sqrt(variance + eps);
    for (0..n) |i| {
        out[i] = (x[i] - mean) * inv_std * gamma[i] + beta[i];
    }
}

// ---- Tests ----

test "SIMD dot product" {
    const a = [_]f32{ 1, 2, 3, 4, 5, 6, 7, 8, 9 };
    const b = [_]f32{ 9, 8, 7, 6, 5, 4, 3, 2, 1 };
    const result = dotProduct(&a, &b);
    // Expected: 1*9+2*8+3*7+4*6+5*5+6*4+7*3+8*2+9*1 = 165
    try std.testing.expectApproxEqAbs(result, 165.0, 0.01);
}

test "softmax sums to 1" {
    var data = [_]f32{ 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0 };
    softmax(&data);
    var sum: f32 = 0.0;
    for (data) |v| sum += v;
    try std.testing.expectApproxEqAbs(sum, 1.0, 0.001);
}
