section .text
global omni_spin_lock
global omni_spin_unlock

; void omni_spin_lock(int* lock_addr)
; RDI contains the pointer to the lock
omni_spin_lock:
    mov eax, 1          ; Value to set (1 = locked)
.retry:
    xchg eax, [rdi]     ; Atomic exchange
    test eax, eax       ; Was it 0 before?
    jz .acquired        ; If yes, we got the lock
    pause               ; CPU hint to optimize spin wait
    jmp .retry          ; Try again
.acquired:
    ret

; void omni_spin_unlock(int* lock_addr)
; RDI contains the pointer to the lock
omni_spin_unlock:
    xor eax, eax        ; 0 = unlocked
    xchg eax, [rdi]     ; Atomic release
    ret
