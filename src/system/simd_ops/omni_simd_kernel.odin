// @omni-layer System | @omni-lang Odin | @omni-batch 17
// @omni-description SIMD math kernel: Odin-native vectorized matrix operations
// with explicit SIMD intrinsics for neural network forward pass.
package omni_simd

import "core:math"
import "core:fmt"

Vec4 :: [4]f32
Mat4x4 :: [4][4]f32

OmniResult :: struct(T: typeid) {
    data: T,
    error: string,
    ok: bool,
}

make_ok :: proc(data: $T) -> OmniResult(T) {
    return OmniResult(T){data = data, error = "", ok = true}
}

make_err :: proc($T: typeid, msg: string) -> OmniResult(T) {
    return OmniResult(T){error = msg, ok = false}
}

// Vectorized dot product using Odin SIMD-style arrays
vec4_dot :: proc(a, b: Vec4) -> f32 {
    result := a * b  // element-wise multiply
    return result[0] + result[1] + result[2] + result[3]
}

vec4_norm :: proc(v: Vec4) -> f32 {
    return math.sqrt(vec4_dot(v, v))
}

vec4_normalize :: proc(v: Vec4) -> Vec4 {
    n := vec4_norm(v)
    if n < 1e-8 { return Vec4{0, 0, 0, 0} }
    inv := 1.0 / n
    return Vec4{v[0]*inv, v[1]*inv, v[2]*inv, v[3]*inv}
}

// Matrix-vector multiply (4x4 * 4)
mat4_mul_vec4 :: proc(m: Mat4x4, v: Vec4) -> Vec4 {
    result: Vec4
    for i in 0..<4 {
        result[i] = vec4_dot(m[i], v)
    }
    return result
}

// ReLU activation on flat buffer
relu_inplace :: proc(data: []f32) {
    for &val in data {
        if val < 0 { val = 0 }
    }
}

// Leaky ReLU
leaky_relu_inplace :: proc(data: []f32, alpha: f32 = 0.01) {
    for &val in data {
        if val < 0 { val *= alpha }
    }
}

// GELU approximation
gelu_inplace :: proc(data: []f32) {
    for &val in data {
        x := val
        // Approximate: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        inner := 0.7978845608 * (x + 0.044715 * x * x * x)
        val = 0.5 * x * (1.0 + math.tanh(inner))
    }
}

// Layer normalization
layer_norm :: proc(data: []f32, eps: f32 = 1e-5) {
    n := f32(len(data))
    mean: f32 = 0
    for val in data { mean += val }
    mean /= n
    variance: f32 = 0
    for val in data {
        d := val - mean
        variance += d * d
    }
    variance /= n
    inv_std := 1.0 / math.sqrt(variance + eps)
    for &val in data {
        val = (val - mean) * inv_std
    }
}

// Cosine similarity between two buffers
cosine_similarity :: proc(a, b: []f32) -> OmniResult(f32) {
    if len(a) != len(b) {
        return make_err(f32, "dimension mismatch")
    }
    dot: f32 = 0; na: f32 = 0; nb: f32 = 0
    for i in 0..<len(a) {
        dot += a[i] * b[i]
        na += a[i] * a[i]
        nb += b[i] * b[i]
    }
    denom := math.sqrt(na) * math.sqrt(nb)
    if denom < 1e-8 { return make_err(f32, "zero norm vector") }
    return make_ok(dot / denom)
}
