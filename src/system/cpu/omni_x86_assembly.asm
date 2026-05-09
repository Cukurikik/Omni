; OMNI System Layer: x86_64 SIMD Optimization (NASM)
; Provides AVX2 fallback mechanisms for tensor core mathematics when GPUs are absent.

section .text
global omni_avx2_dot_product

; omni_avx2_dot_product(float* a, float* b, int n)
; rdi = pointer to array a
; rsi = pointer to array b
; edx = length n
omni_avx2_dot_product:
    vxorps ymm0, ymm0, ymm0    ; Clear accumulator ymm0 (holds sum)
    test edx, edx
    jle .done                  ; If n <= 0, return 0
    
    mov rcx, 0                 ; Index i = 0

.loop:
    cmp rcx, rdx
    jge .reduce                ; If i >= n, break to reduction

    ; Load 8 floats from a and b
    vmovups ymm1, [rdi + rcx*4]
    vmovups ymm2, [rsi + rcx*4]
    
    ; Multiply and accumulate
    vfmadd231ps ymm0, ymm1, ymm2 ; ymm0 += ymm1 * ymm2

    add rcx, 8                 ; i += 8
    jmp .loop

.reduce:
    ; Horizontal sum of ymm0 into xmm0
    vextractf128 xmm1, ymm0, 1
    vaddps xmm0, xmm0, xmm1
    
    vhaddps xmm0, xmm0, xmm0
    vhaddps xmm0, xmm0, xmm0

.done:
    vzeroupper                 ; Clear upper YMM state
    ret                        ; Result is in xmm0
