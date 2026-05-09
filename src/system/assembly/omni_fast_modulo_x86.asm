; OMNI Framework - x86_64 Assembly for Fast Modulo Arithmetic
; Used to accelerate the Grokking dataset generation for algorithmic learning.

section .text
    global omni_fast_mod_add

; Signature: uint32_t omni_fast_mod_add(uint32_t a, uint32_t b, uint32_t p)
; a is in EDI, b is in ESI, p is in EDX
; Returns result in EAX

omni_fast_mod_add:
    mov eax, edi        ; Move 'a' into EAX
    add eax, esi        ; Add 'b' to EAX
    cmp eax, edx        ; Compare (a+b) with 'p'
    jb .done            ; If (a+b) < p, jump to done
    sub eax, edx        ; Else, subtract 'p'
.done:
    ret                 ; Return result
