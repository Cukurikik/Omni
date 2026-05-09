; OMNI MOTHER Production Zero-Mock x86-64 Assembly
; SIMD AVX2 Matrix Transpose for 4x4 float blocks
; Extremely fast, cache-aligned transposition used before MoE routing logic.

section .text
global omni_transpose_4x4_avx2

; void omni_transpose_4x4_avx2(float* src, float* dst);
; rdi = src pointer, rsi = dst pointer

omni_transpose_4x4_avx2:
    ; Load 4 rows of 4 floats (16 bytes each) into XMM registers
    movups xmm0, [rdi]          ; row 0: a0 a1 a2 a3
    movups xmm1, [rdi + 16]     ; row 1: b0 b1 b2 b3
    movups xmm2, [rdi + 32]     ; row 2: c0 c1 c2 c3
    movups xmm3, [rdi + 48]     ; row 3: d0 d1 d2 d3

    ; Interleave and transpose using unpck
    movaps xmm4, xmm0
    unpcklps xmm4, xmm1         ; xmm4: a0 b0 a1 b1
    unpckhps xmm0, xmm1         ; xmm0: a2 b2 a3 b3

    movaps xmm5, xmm2
    unpcklps xmm5, xmm3         ; xmm5: c0 d0 c1 d1
    unpckhps xmm2, xmm3         ; xmm2: c2 d2 c3 d3

    movaps xmm1, xmm4
    shufps xmm1, xmm5, 0x44     ; xmm1: a0 b0 c0 d0 (Row 0 transposed)
    shufps xmm4, xmm5, 0xEE     ; xmm4: a1 b1 c1 d1 (Row 1 transposed)

    movaps xmm3, xmm0
    shufps xmm3, xmm2, 0x44     ; xmm3: a2 b2 c2 d2 (Row 2 transposed)
    shufps xmm0, xmm2, 0xEE     ; xmm0: a3 b3 c3 d3 (Row 3 transposed)

    ; Store results back to dst
    movups [rsi], xmm1
    movups [rsi + 16], xmm4
    movups [rsi + 32], xmm3
    movups [rsi + 48], xmm0

    ret
