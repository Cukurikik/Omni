; OMNI System Layer — x86-64 Assembly SIMD Dot Product
; AVX2-accelerated vector dot product for transformer attention scores.
; Callable from C/C++ via System V ABI.
;
; float omni_avx2_dot_f32(const float* a, const float* b, int64_t n);

section .text
global omni_avx2_dot_f32

; Arguments (System V AMD64 ABI):
;   rdi = const float* a
;   rsi = const float* b
;   rdx = int64_t n (number of elements)
; Returns:
;   xmm0 = float result

omni_avx2_dot_f32:
    push    rbp
    mov     rbp, rsp

    ; Initialize accumulator
    vxorps  ymm0, ymm0, ymm0       ; ymm0 = accumulator (8 floats)
    vxorps  ymm1, ymm1, ymm1       ; ymm1 = secondary accumulator

    mov     rcx, rdx                ; rcx = n
    shr     rcx, 4                  ; rcx = n / 16 (process 16 floats per iteration)
    jz      .remainder8

.loop16:
    ; Load 16 floats from a and b
    vmovups ymm2, [rdi]             ; a[0..7]
    vmovups ymm3, [rdi + 32]        ; a[8..15]
    vmovups ymm4, [rsi]             ; b[0..7]
    vmovups ymm5, [rsi + 32]        ; b[8..15]

    ; Fused multiply-add: acc += a * b
    vfmadd231ps ymm0, ymm2, ymm4   ; ymm0 += a[0..7] * b[0..7]
    vfmadd231ps ymm1, ymm3, ymm5   ; ymm1 += a[8..15] * b[8..15]

    add     rdi, 64
    add     rsi, 64
    dec     rcx
    jnz     .loop16

    ; Merge accumulators
    vaddps  ymm0, ymm0, ymm1

.remainder8:
    ; Process remaining 8-float chunks
    mov     rcx, rdx
    and     rcx, 15
    shr     rcx, 3                  ; remaining / 8
    jz      .remainder_scalar

    vmovups ymm2, [rdi]
    vmovups ymm3, [rsi]
    vfmadd231ps ymm0, ymm2, ymm3
    add     rdi, 32
    add     rsi, 32

.remainder_scalar:
    ; Horizontal sum of ymm0
    vextractf128 xmm1, ymm0, 1     ; upper 128 bits
    vaddps  xmm0, xmm0, xmm1       ; xmm0 = sum of upper and lower
    vhaddps xmm0, xmm0, xmm0       ; horizontal add
    vhaddps xmm0, xmm0, xmm0       ; final horizontal add

    ; Process remaining scalar elements
    mov     rcx, rdx
    and     rcx, 7                  ; remaining mod 8
    jz      .done

.scalar_loop:
    vmovss  xmm1, [rdi]
    vmulss  xmm1, xmm1, [rsi]
    vaddss  xmm0, xmm0, xmm1
    add     rdi, 4
    add     rsi, 4
    dec     rcx
    jnz     .scalar_loop

.done:
    vzeroupper                      ; Clear upper YMM to avoid SSE penalty
    pop     rbp
    ret
