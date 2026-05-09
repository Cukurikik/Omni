; OMNI System Layer — ARM64 NEON SIMD Dot Product
; AArch64 NEON-accelerated vector dot product for mobile/edge inference.
; float omni_neon_dot_f32(const float* a, const float* b, int64_t n);

.global omni_neon_dot_f32
.type omni_neon_dot_f32, %function

// x0 = const float* a
// x1 = const float* b
// x2 = int64_t n
// Returns: s0 = float result

omni_neon_dot_f32:
    movi    v0.4s, #0               // v0 = accumulator (4 floats)
    movi    v1.4s, #0               // v1 = secondary accumulator

    // Process 8 floats per iteration (2x NEON registers)
    lsr     x3, x2, #3             // x3 = n / 8
    cbz     x3, .Lremainder4

.Lloop8:
    ld1     {v2.4s, v3.4s}, [x0], #32   // Load 8 floats from a
    ld1     {v4.4s, v5.4s}, [x1], #32   // Load 8 floats from b
    fmla    v0.4s, v2.4s, v4.4s         // v0 += a[0..3] * b[0..3]
    fmla    v1.4s, v3.4s, v5.4s         // v1 += a[4..7] * b[4..7]
    subs    x3, x3, #1
    b.ne    .Lloop8

    fadd    v0.4s, v0.4s, v1.4s         // Merge accumulators

.Lremainder4:
    // Process remaining 4-float chunk
    and     x3, x2, #7
    lsr     x3, x3, #2
    cbz     x3, .Lscalar

    ld1     {v2.4s}, [x0], #16
    ld1     {v3.4s}, [x1], #16
    fmla    v0.4s, v2.4s, v3.4s

.Lscalar:
    // Horizontal sum of v0
    faddp   v0.4s, v0.4s, v0.4s        // Pairwise add
    faddp   s0, v0.2s                   // Final pairwise add -> s0

    // Handle remaining scalar elements
    and     x3, x2, #3
    cbz     x3, .Ldone

.Lscalar_loop:
    ldr     s1, [x0], #4
    ldr     s2, [x1], #4
    fmadd   s0, s1, s2, s0
    subs    x3, x3, #1
    b.ne    .Lscalar_loop

.Ldone:
    ret
