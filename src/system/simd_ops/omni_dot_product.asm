; @omni-layer System | @omni-lang Assembly (x86-64 AVX2) | @omni-batch 17
; @omni-description SIMD dot product: AVX2-accelerated float32 dot product
; for embedding similarity. Uses 256-bit YMM registers.
; Calling convention: System V AMD64
;   rdi = pointer to float32 array A
;   rsi = pointer to float32 array B
;   rdx = count (number of f32 elements, must be multiple of 8)
;   Returns: xmm0 = dot product result (f32)

section .text
global omni_dot_product_avx2
global omni_vector_norm_avx2
global omni_saxpy_avx2

; float omni_dot_product_avx2(const float* a, const float* b, int64_t n)
omni_dot_product_avx2:
    push    rbp
    mov     rbp, rsp
    vxorps  ymm0, ymm0, ymm0       ; accumulator = 0
    xor     rcx, rcx                ; i = 0
    mov     rax, rdx
    and     rax, ~7                 ; n aligned to 8

.loop_avx:
    cmp     rcx, rax
    jge     .tail
    vmovups ymm1, [rdi + rcx*4]    ; load 8 floats from A
    vmovups ymm2, [rsi + rcx*4]    ; load 8 floats from B
    vfmadd231ps ymm0, ymm1, ymm2  ; acc += A[i:i+8] * B[i:i+8]
    add     rcx, 8
    jmp     .loop_avx

.tail:
    ; Horizontal sum of ymm0 (8 floats -> 1 float)
    vextractf128 xmm1, ymm0, 1    ; upper 128 bits
    vaddps  xmm0, xmm0, xmm1      ; add upper to lower
    vhaddps xmm0, xmm0, xmm0      ; horizontal add
    vhaddps xmm0, xmm0, xmm0      ; final horizontal add

    ; Handle remaining elements (n % 8)
    cmp     rcx, rdx
    jge     .done
.scalar_loop:
    vmovss  xmm1, [rdi + rcx*4]
    vmovss  xmm2, [rsi + rcx*4]
    vfmadd231ss xmm0, xmm1, xmm2
    inc     rcx
    cmp     rcx, rdx
    jl      .scalar_loop

.done:
    vzeroupper
    pop     rbp
    ret

; float omni_vector_norm_avx2(const float* v, int64_t n)
omni_vector_norm_avx2:
    push    rbp
    mov     rbp, rsp
    mov     rdx, rsi                ; n
    mov     rsi, rdi                ; b = a (self dot product)
    call    omni_dot_product_avx2
    vsqrtss xmm0, xmm0, xmm0      ; sqrt(dot(v, v))
    pop     rbp
    ret

; void omni_saxpy_avx2(float* y, const float* x, float alpha, int64_t n)
; y[i] += alpha * x[i]
; rdi=y, rsi=x, xmm0=alpha, rdx=n
omni_saxpy_avx2:
    push    rbp
    mov     rbp, rsp
    vbroadcastss ymm2, xmm0        ; broadcast alpha to all 8 lanes
    xor     rcx, rcx
    mov     rax, rdx
    and     rax, ~7

.saxpy_loop:
    cmp     rcx, rax
    jge     .saxpy_tail
    vmovups ymm0, [rdi + rcx*4]    ; load y
    vmovups ymm1, [rsi + rcx*4]    ; load x
    vfmadd231ps ymm0, ymm1, ymm2  ; y += alpha * x
    vmovups [rdi + rcx*4], ymm0    ; store y
    add     rcx, 8
    jmp     .saxpy_loop

.saxpy_tail:
    cmp     rcx, rdx
    jge     .saxpy_done
.saxpy_scalar:
    vmovss  xmm0, [rdi + rcx*4]
    vmovss  xmm1, [rsi + rcx*4]
    vfmadd231ss xmm0, xmm1, xmm2
    vmovss  [rdi + rcx*4], xmm0
    inc     rcx
    cmp     rcx, rdx
    jl      .saxpy_scalar

.saxpy_done:
    vzeroupper
    pop     rbp
    ret
