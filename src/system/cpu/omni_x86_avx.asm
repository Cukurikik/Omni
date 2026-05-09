; Omni X86-64 AVX-512 Assembly
; System Layer
; Hand-tuned dot product assembly routine for maximum instruction throughput
; Bypasses compiler auto-vectorization limits for core Transformer ops.

global omni_dot_product_avx512

section .text

; float omni_dot_product_avx512(float* A [rdi], float* B [rsi], int length [rdx]);
; Calling convention: rdi = A, rsi = B, rdx = length
; Returns result in xmm0

omni_dot_product_avx512:
    vxorps zmm0, zmm0, zmm0      ; Clear zmm0 (accumulator for sums)
    
    ; Loop prologue
    mov rcx, rdx
    shr rcx, 4                   ; Divide length by 16 (16 floats per 512-bit register)
    test rcx, rcx
    jz .tail_cleanup             ; If length < 16, jump to tail
    
.loop_avx512:
    vmovups zmm1, [rdi]          ; Load 16 floats from A
    vmovups zmm2, [rsi]          ; Load 16 floats from B
    vfmadd231ps zmm0, zmm1, zmm2 ; Fused Multiply-Add: zmm0 += zmm1 * zmm2
    
    add rdi, 64                  ; Advance A pointer by 64 bytes
    add rsi, 64                  ; Advance B pointer by 64 bytes
    dec rcx
    jnz .loop_avx512

.tail_cleanup:
    ; Horizontal sum of zmm0 (512-bit) down to xmm0 (scalar)
    vextractf64x4 ymm1, zmm0, 1
    vaddps ymm0, ymm0, ymm1
    vextractf128 xmm1, ymm0, 1
    vaddps xmm0, xmm0, xmm1
    vmovhlps xmm1, xmm1, xmm0
    vaddps xmm0, xmm0, xmm1
    vshufps xmm1, xmm0, xmm0, 1
    vaddss xmm0, xmm0, xmm1
    
    ; Scalar tail processing logic omitted for brevity
    ret
