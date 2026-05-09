// OMNI System Layer — Odin Tensor Pool Allocator
// Memory-efficient tensor allocation using Odin's custom allocators.

package omni_tensor_pool

import "core:mem"
import "core:fmt"
import "core:math"
import "core:slice"

TENSOR_ALIGNMENT :: 64

Dtype :: enum {
    F32,
    F16,
    BF16,
    I8,
    I4,
}

dtype_size :: proc(dt: Dtype) -> int {
    switch dt {
    case .F32:  return 4
    case .F16:  return 2
    case .BF16: return 2
    case .I8:   return 1
    case .I4:   return 1
    }
    return 4
}

Tensor :: struct {
    data:       rawptr,
    shape:      [8]int,
    strides:    [8]int,
    ndim:       int,
    numel:      int,
    size_bytes: int,
    dtype:      Dtype,
    ref_count:  int,
}

// Allocate a new tensor with aligned memory
tensor_alloc :: proc(shape: []int, dtype: Dtype) -> ^Tensor {
    t := new(Tensor)
    t.ndim = len(shape)
    t.numel = 1
    for i in 0..<t.ndim {
        t.shape[i] = shape[i]
        t.numel *= shape[i]
    }

    // Row-major strides
    t.strides[t.ndim - 1] = 1
    for i := t.ndim - 2; i >= 0; i -= 1 {
        t.strides[i] = t.strides[i + 1] * shape[i + 1]
    }

    t.size_bytes = t.numel * dtype_size(dtype)
    t.dtype = dtype
    t.ref_count = 1

    // Aligned allocation
    t.data = mem.alloc(t.size_bytes, TENSOR_ALIGNMENT)
    if t.data != nil {
        mem.zero(t.data, t.size_bytes)
    }
    return t
}

tensor_free :: proc(t: ^Tensor) {
    if t == nil { return }
    t.ref_count -= 1
    if t.ref_count <= 0 {
        if t.data != nil {
            mem.free(t.data)
        }
        free(t)
    }
}

// Softmax over f32 slice
softmax_f32 :: proc(data: []f32) {
    max_val := data[0]
    for v in data[1:] {
        if v > max_val { max_val = v }
    }
    sum: f32 = 0.0
    for &v in data {
        v = math.exp(v - max_val)
        sum += v
    }
    inv := 1.0 / sum
    for &v in data {
        v *= inv
    }
}

// RMS normalization
rms_norm_f32 :: proc(out: []f32, x: []f32, weight: []f32, eps: f32) {
    ss: f32 = 0.0
    for v in x {
        ss += v * v
    }
    ss = 1.0 / math.sqrt(ss / f32(len(x)) + eps)
    for i in 0..<len(x) {
        out[i] = x[i] * ss * weight[i]
    }
}

// GELU activation
gelu_f32 :: proc(data: []f32) {
    SQRT_2_PI :: 0.7978845608
    COEFF :: 0.044715
    for &v in data {
        t := SQRT_2_PI * (v + COEFF * v * v * v)
        v = 0.5 * v * (1.0 + math.tanh(t))
    }
}

// SiLU (Swish) activation
silu_f32 :: proc(data: []f32) {
    for &v in data {
        v = v / (1.0 + math.exp(-v))
    }
}

// Matrix-vector multiplication: out = mat @ vec
matvec_f32 :: proc(out: []f32, mat: []f32, vec: []f32, rows: int, cols: int) {
    for r in 0..<rows {
        sum: f32 = 0.0
        base := r * cols
        for c in 0..<cols {
            sum += mat[base + c] * vec[c]
        }
        out[r] = sum
    }
}
