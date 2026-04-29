// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Odin Language — System Layer (OMNI Zero-Mock Implementation)
// Implements deterministic SIMD-width vector mathematics for 4-component f32 vectors.
// Absorbs patterns from: github.com/odin-lang/Odin core:math/linalg

package omni_odin_simd

Vec4 :: struct {
    x, y, z, w: f32,
}

Simd_Result :: struct {
    value: Vec4,
    is_ok: bool,
    error: string,
}

Scalar_Result :: struct {
    value: f32,
    is_ok: bool,
    error: string,
}

// Exact SIMD-lane dot product: sum of component-wise products.
// d = a.x*b.x + a.y*b.y + a.z*b.z + a.w*b.w
vec4_dot :: proc(a: Vec4, b: Vec4) -> f32 {
    return a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w
}

// Component-wise fused multiply-add: result = a * b + c
// Maps directly to FMA SIMD instruction when available.
vec4_fma :: proc(a: Vec4, b: Vec4, c: Vec4) -> Vec4 {
    return Vec4{
        x = a.x * b.x + c.x,
        y = a.y * b.y + c.y,
        z = a.z * b.z + c.z,
        w = a.w * b.w + c.w,
    }
}

// Euclidean L2 norm: sqrt(dot(v, v))
vec4_length :: proc(v: Vec4) -> Scalar_Result {
    sq := vec4_dot(v, v)
    if sq < 0.0 {
        return Scalar_Result{value = 0.0, is_ok = false, error = "Negative squared norm is mathematically impossible."}
    }
    import "core:math"
    return Scalar_Result{value = math.sqrt(sq), is_ok = true, error = ""}
}

// Unit normalization with zero-division protection.
vec4_normalize :: proc(v: Vec4) -> Simd_Result {
    sq := vec4_dot(v, v)
    if sq == 0.0 {
        return Simd_Result{value = Vec4{}, is_ok = false, error = "Cannot normalize zero-length vector."}
    }
    import "core:math"
    inv_len := 1.0 / math.sqrt(sq)
    return Simd_Result{
        value = Vec4{
            x = v.x * inv_len,
            y = v.y * inv_len,
            z = v.z * inv_len,
            w = v.w * inv_len,
        },
        is_ok = true,
        error = "",
    }
}

// Linear interpolation: lerp(a, b, t) = a + t*(b - a)
vec4_lerp :: proc(a: Vec4, b: Vec4, t: f32) -> Simd_Result {
    if t < 0.0 || t > 1.0 {
        return Simd_Result{value = Vec4{}, is_ok = false, error = "Interpolation parameter t must be in [0.0, 1.0]."}
    }
    return Simd_Result{
        value = Vec4{
            x = a.x + t * (b.x - a.x),
            y = a.y + t * (b.y - a.y),
            z = a.z + t * (b.z - a.z),
            w = a.w + t * (b.w - a.w),
        },
        is_ok = true,
        error = "",
    }
}
