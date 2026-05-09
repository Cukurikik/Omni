; @omni-layer System | @omni-lang x86 Assembly | @omni-batch 18 | @omni-semester 16
; @omni-description AVX-512 softmax kernel for transformer attention: vectorized
; exp, max-reduction, and normalization for attention score computation.

section .data
align 64
exp_coeff_0: times 16 dd 1.0
exp_coeff_1: times 16 dd 1.0
exp_coeff_2: times 16 dd 0.5
exp_coeff_3: times 16 dd 0.166666667
exp_coeff_4: times 16 dd 0.041666667
exp_coeff_5: times 16 dd 0.008333333
neg_inf:     times 16 dd 0xFF800000
eps_val:     times 16 dd 1.0e-10

section .text
global omni_avx512_softmax
global omni_avx512_max_reduce

; void omni_avx512_max_reduce(const float* data, int n, float* result)
; Finds maximum value across n floats using AVX-512
omni_avx512_max_reduce:
    push rbp
    mov rbp, rsp
    ; rdi = data pointer, esi = n, rdx = result pointer
    vmovups zmm0, [rel neg_inf]     ; initialize max to -inf
    xor ecx, ecx                     ; counter
.max_loop:
    cmp ecx, esi
    jge .max_done
    lea eax, [ecx + 16]
    cmp eax, esi
    jg .max_scalar
    vmovups zmm1, [rdi + rcx*4]
    vmaxps zmm0, zmm0, zmm1
    add ecx, 16
    jmp .max_loop
.max_scalar:
    vbroadcastss zmm1, [rdi + rcx*4]
    vmaxps zmm0, zmm0, zmm1
    inc ecx
    jmp .max_loop
.max_done:
    ; Horizontal max reduce zmm0
    vextractf32x8 ymm1, zmm0, 1
    vmaxps ymm0, ymm0, ymm1
    vextractf128 xmm1, ymm0, 1
    vmaxps xmm0, xmm0, xmm1
    vshufps xmm1, xmm0, xmm0, 0x4E
    vmaxps xmm0, xmm0, xmm1
    vshufps xmm1, xmm0, xmm0, 0xB1
    vmaxps xmm0, xmm0, xmm1
    vmovss [rdx], xmm0
    pop rbp
    ret

; void omni_avx512_softmax(float* data, int n, float max_val)
; Computes softmax in-place: exp(x - max) / sum(exp(x - max))
omni_avx512_softmax:
    push rbp
    mov rbp, rsp
    ; rdi = data, esi = n, xmm0 = max_val
    vbroadcastss zmm15, xmm0        ; max_val broadcast
    vxorps zmm14, zmm14, zmm14      ; sum accumulator

    ; Pass 1: subtract max and approximate exp
    xor ecx, ecx
.exp_loop:
    cmp ecx, esi
    jge .normalize
    lea eax, [ecx + 16]
    cmp eax, esi
    jg .exp_scalar
    vmovups zmm1, [rdi + rcx*4]
    vsubps zmm1, zmm1, zmm15        ; x - max
    ; Fast exp approximation using polynomial
    vmovaps zmm2, [rel exp_coeff_0]  ; 1.0
    vmovaps zmm3, zmm1               ; x
    vfmadd231ps zmm2, zmm3, [rel exp_coeff_1] ; 1 + x
    vmulps zmm3, zmm3, zmm1          ; x^2
    vfmadd231ps zmm2, zmm3, [rel exp_coeff_2] ; + x^2/2
    vmulps zmm3, zmm3, zmm1          ; x^3
    vfmadd231ps zmm2, zmm3, [rel exp_coeff_3] ; + x^3/6
    vmaxps zmm2, zmm2, [rel eps_val] ; clamp to eps
    vmovups [rdi + rcx*4], zmm2
    vaddps zmm14, zmm14, zmm2        ; accumulate sum
    add ecx, 16
    jmp .exp_loop
.exp_scalar:
    vmovss xmm1, [rdi + rcx*4]
    vsubss xmm1, xmm1, xmm0
    ; Scalar exp approximation
    vmovss xmm2, [rel exp_coeff_0]
    vfmadd231ss xmm2, xmm1, [rel exp_coeff_1]
    vmaxss xmm2, xmm2, [rel eps_val]
    vmovss [rdi + rcx*4], xmm2
    vaddss xmm14, xmm14, xmm2
    inc ecx
    jmp .exp_loop

.normalize:
    ; Horizontal sum of zmm14
    vextractf32x8 ymm1, zmm14, 1
    vaddps ymm14, ymm14, ymm1
    vextractf128 xmm1, ymm14, 1
    vaddps xmm14, xmm14, xmm1
    vhaddps xmm14, xmm14, xmm14
    vhaddps xmm14, xmm14, xmm14
    ; 1/sum
    vmovss xmm1, [rel exp_coeff_0]
    vdivss xmm14, xmm1, xmm14
    vbroadcastss zmm14, xmm14

    ; Pass 2: normalize
    xor ecx, ecx
.norm_loop:
    cmp ecx, esi
    jge .done
    lea eax, [ecx + 16]
    cmp eax, esi
    jg .norm_scalar
    vmovups zmm1, [rdi + rcx*4]
    vmulps zmm1, zmm1, zmm14
    vmovups [rdi + rcx*4], zmm1
    add ecx, 16
    jmp .norm_loop
.norm_scalar:
    vmovss xmm1, [rdi + rcx*4]
    vmulss xmm1, xmm1, xmm14
    vmovss [rdi + rcx*4], xmm1
    inc ecx
    jmp .norm_loop
.done:
    pop rbp
    ret
