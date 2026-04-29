; OMNI Divine Memory Integration: Inspired by txtai
; System Layer - x86_64 AVX2 Assembly for ultra-fast Vector Dot Product (Cosine Similarity base)
; Strict physical hardware execution for embedding comparisons.

global _omni_simd_dot_product
section .text

; _omni_simd_dot_product(const float* a, const float* b, size_t length)
; rdi = a (pointer to first vector)
; rsi = b (pointer to second vector)
; rdx = length (number of floats, MUST be multiple of 8 for AVX)

_omni_simd_dot_product:
    ; Initialize accumulator ymm0 to zero
    vxorps ymm0, ymm0, ymm0
    
    ; Check if length is 0
    test rdx, rdx
    jz .done

.loop:
    ; Load 8 floats from a into ymm1
    vmovups ymm1, [rdi]
    
    ; Load 8 floats from b into ymm2
    vmovups ymm2, [rsi]
    
    ; Multiply ymm1 and ymm2, store in ymm1
    vmulps ymm1, ymm1, ymm2
    
    ; Add result to accumulator ymm0
    vaddps ymm0, ymm0, ymm1
    
    ; Advance pointers by 32 bytes (8 floats * 4 bytes)
    add rdi, 32
    add rsi, 32
    
    ; Decrement length by 8
    sub rdx, 8
    jnz .loop

.done:
    ; Horizontal add to sum the 8 floats in ymm0 down to the lowest scalar float
    vhaddps ymm0, ymm0, ymm0
    vhaddps ymm0, ymm0, ymm0
    ; The lowest 32 bits of xmm0 now hold the sum of the lower 4 floats
    ; Extract the high 128 bits and add
    vextractf128 xmm1, ymm0, 1
    vaddps xmm0, xmm0, xmm1
    
    ; Return value is in xmm0
    ret
