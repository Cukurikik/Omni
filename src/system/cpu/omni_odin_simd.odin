package omni_simd

import "core:fmt"
import "core:math"
import "core:simd"

// Omni SIMD Vectorizer (Odin)
// System Layer
// Direct CPU-SIMD intrinsics using Odin for high-performance tensor ops.
// Replaces standard math loops with parallel 4x/8x packed execution.

// 256-bit wide AVX vector (8 x f32)
#simd f32x8 :: #simd[8]f32

// Highly optimized dot product using Odin SIMD features
export "c" omni_dot_product_simd :: proc(a, b: ^f32, length: int) -> f32 {
    sum_vec: f32x8 = 0.0
    
    // Process 8 elements at a time
    vec_len := length - (length % 8)
    
    a_ptr := cast(^f32x8) a
    b_ptr := cast(^f32x8) b
    
    for i := 0; i < vec_len / 8; i += 1 {
        // Multiply and accumulate
        sum_vec += a_ptr[i] * b_ptr[i]
    }
    
    // Horizontal addition of the 8 float lanes
    final_sum: f32 = sum_vec[0] + sum_vec[1] + sum_vec[2] + sum_vec[3] + 
                     sum_vec[4] + sum_vec[5] + sum_vec[6] + sum_vec[7]
                     
    // Process remaining tail elements
    for i := vec_len; i < length; i += 1 {
        final_sum += mem_ptr_offset(a, i)^ * mem_ptr_offset(b, i)^
    }
    
    return final_sum
}

mem_ptr_offset :: proc(ptr: ^f32, offset: int) -> ^f32 {
    return cast(^f32)(cast(uintptr)ptr + uintptr(offset * size_of(f32)))
}
