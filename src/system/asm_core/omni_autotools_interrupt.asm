; Omni AutoTools Interrupt (x86 Assembly / NASM)
; System Layer: Bare-metal trap for executing safe tool boundaries.

section .text
global _omni_autotools_trap

_omni_autotools_trap:
    ; Input: eax = tool_id, ebx = permission_level
    ; Output: eax = 1 (safe), 0 (deny)
    
    cmp ebx, 0          ; Level 0 is kernel/root
    je .deny            ; AutoTools cannot run as root
    
    mov eax, 1          ; Safe execution
    ret

.deny:
    mov eax, 0
    ret
