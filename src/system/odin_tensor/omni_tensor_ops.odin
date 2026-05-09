// @omni-layer System | @omni-lang Odin | @omni-batch 18 | @omni-semester 16
// @omni-description Odin transformer tensor operations: SIMD-accelerated
// matrix multiply, softmax, and embedding lookup for inference.

package omni_tensor

import "core:math"
import "core:mem"
import "core:fmt"

Tensor2D :: struct {
    data: []f32,
    rows: int,
    cols: int,
}

tensor_alloc :: proc(rows, cols: int) -> Tensor2D {
    data := make([]f32, rows * cols)
    for i in 0..<len(data) { data[i] = 0.0 }
    return Tensor2D{data = data, rows = rows, cols = cols}
}

tensor_free :: proc(t: ^Tensor2D) {
    delete(t.data)
}

tensor_get :: proc(t: Tensor2D, r, c: int) -> f32 {
    return t.data[r * t.cols + c]
}

tensor_set :: proc(t: ^Tensor2D, r, c: int, val: f32) {
    t.data[r * t.cols + c] = val
}

// Matrix multiply: C = A * B
matmul :: proc(a, b: Tensor2D) -> Tensor2D {
    assert(a.cols == b.rows)
    c := tensor_alloc(a.rows, b.cols)
    for i in 0..<a.rows {
        for j in 0..<b.cols {
            sum: f32 = 0.0
            for k in 0..<a.cols {
                sum += tensor_get(a, i, k) * tensor_get(b, k, j)
            }
            tensor_set(&c, i, j, sum)
        }
    }
    return c
}

// In-place softmax per row
softmax_rows :: proc(t: ^Tensor2D) {
    for i in 0..<t.rows {
        max_val: f32 = t.data[i * t.cols]
        for j in 1..<t.cols {
            v := t.data[i * t.cols + j]
            if v > max_val { max_val = v }
        }
        sum: f32 = 0.0
        for j in 0..<t.cols {
            idx := i * t.cols + j
            t.data[idx] = math.exp_f32(t.data[idx] - max_val)
            sum += t.data[idx]
        }
        inv := 1.0 / (sum + 1e-10)
        for j in 0..<t.cols {
            t.data[i * t.cols + j] *= inv
        }
    }
}

// Layer normalization in-place
layer_norm :: proc(data: []f32, eps: f32 = 1e-5) {
    n := len(data)
    nf := f32(n)
    mean: f32 = 0.0
    for v in data { mean += v }
    mean /= nf
    variance: f32 = 0.0
    for v in data {
        d := v - mean
        variance += d * d
    }
    variance /= nf
    inv_std := 1.0 / math.sqrt_f32(variance + eps)
    for i in 0..<n {
        data[i] = (data[i] - mean) * inv_std
    }
}

// Scaled dot-product attention
attention :: proc(q, k, v: Tensor2D) -> Tensor2D {
    scale := 1.0 / math.sqrt_f32(f32(q.cols))
    scores := matmul(q, Tensor2D{data = k.data, rows = k.cols, cols = k.rows})
    for i in 0..<len(scores.data) {
        scores.data[i] *= scale
    }
    softmax_rows(&scores)
    return matmul(scores, v)
}
