// omni_simd_math.zig — Vectorized Math Operations
// Inspired by: OMNI High-Performance System Layer Requirements
// Layer: System / Zig
//
// Implements highly optimized, SIMD-accelerated mathematical operations
// critical for tensor calculations (softmax, dot product, normalizations).

const std = @import("std");

/// Computes the dot product of two f32 vectors using SIMD instructions.
pub fn dotProductSIMD(a: []const f32, b: []const f32) f32 {
    std.debug.assert(a.len == b.len);
    
    var sum: f32 = 0.0;
    var i: usize = 0;
    
    // Process in chunks of 8 floats (256-bit AVX/SIMD vector width)
    const vec_len = 8;
    const V = @Vector(vec_len, f32);
    
    var sum_vec = @as(V, @splat(0.0));
    
    while (i + vec_len <= a.len) : (i += vec_len) {
        const va: V = a[i..][0..vec_len].*;
        const vb: V = b[i..][0..vec_len].*;
        sum_vec += va * vb;
    }
    
    // Reduce the SIMD vector
    sum = @reduce(.Add, sum_vec);
    
    // Handle the remainder
    while (i < a.len) : (i += 1) {
        sum += a[i] * b[i];
    }
    
    return sum;
}

/// Computes an in-place Softmax over an array of f32 using SIMD.
pub fn softmaxSIMD(data: []f32) void {
    if (data.len == 0) return;
    
    // 1. Find max for numerical stability
    var max_val: f32 = data[0];
    for (data) |val| {
        if (val > max_val) max_val = val;
    }
    
    // 2. Exponentiate and sum
    var sum_exp: f32 = 0.0;
    for (data) |*val| {
        val.* = @exp(val.* - max_val);
        sum_exp += val.*;
    }
    
    // 3. Normalize
    const inv_sum = 1.0 / sum_exp;
    var i: usize = 0;
    const vec_len = 8;
    const V = @Vector(vec_len, f32);
    const inv_sum_vec = @as(V, @splat(inv_sum));
    
    while (i + vec_len <= data.len) : (i += vec_len) {
        var vd: V = data[i..][0..vec_len].*;
        vd *= inv_sum_vec;
        data[i..][0..vec_len].* = vd;
    }
    
    while (i < data.len) : (i += 1) {
        data[i] *= inv_sum;
    }
}

// Exported for C FFI to be callable from Rust or C++
export fn omni_dot_product_f32(a_ptr: [*]const f32, b_ptr: [*]const f32, len: usize) f32 {
    const a_slice = a_ptr[0..len];
    const b_slice = b_ptr[0..len];
    return dotProductSIMD(a_slice, b_slice);
}

export fn omni_softmax_f32(data_ptr: [*]f32, len: usize) void {
    const data_slice = data_ptr[0..len];
    softmaxSIMD(data_slice);
}
