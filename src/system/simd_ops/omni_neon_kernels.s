; @omni-layer System | @omni-lang Assembly (ARM AArch64) | @omni-batch 17
; @omni-description ARM NEON dot product: AArch64 NEON SIMD-accelerated
; float32 dot product for mobile/edge inference on ARM processors.
; Calling convention: AAPCS64
;   x0 = pointer to float32 array A
;   x1 = pointer to float32 array B
;   x2 = count (number of f32 elements, should be multiple of 4)
;   Returns: s0 = dot product result (f32)

    .arch armv8-a+simd
    .text
    .global omni_dot_product_neon
    .global omni_vector_add_neon
    .global omni_relu_neon

// float omni_dot_product_neon(const float* a, const float* b, int64_t n)
omni_dot_product_neon:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp
    movi    v0.4s, #0                   // acc = {0,0,0,0}
    mov     x3, x2
    and     x3, x3, #~3                // n aligned to 4

.loop_neon:
    cbz     x3, .tail_neon
    ld1     {v1.4s}, [x0], #16         // load 4 floats from A
    ld1     {v2.4s}, [x1], #16         // load 4 floats from B
    fmla    v0.4s, v1.4s, v2.4s        // acc += A[i:i+4] * B[i:i+4]
    sub     x3, x3, #4
    b       .loop_neon

.tail_neon:
    // Horizontal add: v0 = {a,b,c,d} -> a+b+c+d
    faddp   v0.4s, v0.4s, v0.4s        // {a+b, c+d, a+b, c+d}
    faddp   s0, v0.2s                  // s0 = (a+b) + (c+d)

    // Handle remaining elements (n % 4)
    and     x3, x2, #3
.scalar_neon:
    cbz     x3, .done_neon
    ldr     s1, [x0], #4
    ldr     s2, [x1], #4
    fmadd   s0, s1, s2, s0
    sub     x3, x3, #1
    b       .scalar_neon

.done_neon:
    ldp     x29, x30, [sp], #16
    ret

// void omni_vector_add_neon(float* out, const float* a, const float* b, int64_t n)
omni_vector_add_neon:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp
    mov     x4, x3
    and     x4, x4, #~3

.vadd_loop:
    cbz     x4, .vadd_tail
    ld1     {v0.4s}, [x1], #16
    ld1     {v1.4s}, [x2], #16
    fadd    v2.4s, v0.4s, v1.4s
    st1     {v2.4s}, [x0], #16
    sub     x4, x4, #4
    b       .vadd_loop

.vadd_tail:
    and     x4, x3, #3
.vadd_scalar:
    cbz     x4, .vadd_done
    ldr     s0, [x1], #4
    ldr     s1, [x2], #4
    fadd    s2, s0, s1
    str     s2, [x0], #4
    sub     x4, x4, #1
    b       .vadd_scalar

.vadd_done:
    ldp     x29, x30, [sp], #16
    ret

// void omni_relu_neon(float* data, int64_t n)
// ReLU: data[i] = max(0, data[i])
omni_relu_neon:
    stp     x29, x30, [sp, #-16]!
    mov     x29, sp
    movi    v31.4s, #0                  // zero vector
    mov     x2, x1
    and     x2, x2, #~3

.relu_loop:
    cbz     x2, .relu_tail
    ld1     {v0.4s}, [x0]
    fmax    v0.4s, v0.4s, v31.4s       // max(data, 0)
    st1     {v0.4s}, [x0], #16
    sub     x2, x2, #4
    b       .relu_loop

.relu_tail:
    and     x2, x1, #3
.relu_scalar:
    cbz     x2, .relu_done
    ldr     s0, [x0]
    fmax    s0, s0, s31
    str     s0, [x0], #4
    sub     x2, x2, #1
    b       .relu_scalar

.relu_done:
    ldp     x29, x30, [sp], #16
    ret
