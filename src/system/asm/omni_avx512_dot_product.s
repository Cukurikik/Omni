// OMNI System — x86-64 Assembly SIMD Dot Product
// AVX-512 vectorized dot product for extreme throughput.

.intel_syntax noprefix
.global omni_dot_product_avx512
.global omni_dot_product_avx2

.section .text

// float omni_dot_product_avx512(const float* a, const float* b, int n)
// rdi = a, rsi = b, edx = n
omni_dot_product_avx512:
    vxorps zmm0, zmm0, zmm0    // accumulator
    xor ecx, ecx                // i = 0
    mov eax, edx
    and eax, ~15                // n & ~15 (round down to 16)
.avx512_loop:
    cmp ecx, eax
    jge .avx512_remainder
    vmovups zmm1, [rdi + rcx*4]
    vmovups zmm2, [rsi + rcx*4]
    vfmadd231ps zmm0, zmm1, zmm2
    add ecx, 16
    jmp .avx512_loop
.avx512_remainder:
    // Horizontal reduce zmm0
    vextractf64x4 ymm1, zmm0, 1
    vaddps ymm0, ymm0, ymm1
    vextractf128 xmm1, ymm0, 1
    vaddps xmm0, xmm0, xmm1
    vhaddps xmm0, xmm0, xmm0
    vhaddps xmm0, xmm0, xmm0
    // Handle remaining elements
.avx512_scalar:
    cmp ecx, edx
    jge .avx512_done
    vmovss xmm1, [rdi + rcx*4]
    vmovss xmm2, [rsi + rcx*4]
    vfmadd231ss xmm0, xmm1, xmm2
    inc ecx
    jmp .avx512_scalar
.avx512_done:
    ret

// float omni_dot_product_avx2(const float* a, const float* b, int n)
omni_dot_product_avx2:
    vxorps ymm0, ymm0, ymm0
    xor ecx, ecx
    mov eax, edx
    and eax, ~7
.avx2_loop:
    cmp ecx, eax
    jge .avx2_remainder
    vmovups ymm1, [rdi + rcx*4]
    vmovups ymm2, [rsi + rcx*4]
    vfmadd231ps ymm0, ymm1, ymm2
    add ecx, 8
    jmp .avx2_loop
.avx2_remainder:
    vextractf128 xmm1, ymm0, 1
    vaddps xmm0, xmm0, xmm1
    vhaddps xmm0, xmm0, xmm0
    vhaddps xmm0, xmm0, xmm0
.avx2_scalar:
    cmp ecx, edx
    jge .avx2_done
    vmovss xmm1, [rdi + rcx*4]
    vmovss xmm2, [rsi + rcx*4]
    vfmadd231ss xmm0, xmm1, xmm2
    inc ecx
    jmp .avx2_scalar
.avx2_done:
    vzeroupper
    ret
