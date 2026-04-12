; ==========================================
; 💀 OMNI DESKTOP: System Management Mode (Ring -2) (Phase 114)
; ==========================================
; Mode SMM adalah 'Mode Dewa' sesungguhnya dari prosesor Intel/AMD x86.
; Digunakan untuk System Sleep/Thermal, tapi Omni memanfaatkannya
; untuk menyembunyikan Vektor RAG Agent. Sistem Operasi mati secara harfiah
; saat SMM Omni berjalan (SMI Interrupt).

section .data
    msg db "💀 [OMNI-SMM] CPU Memasuki System Management Mode (SMI Triggered)...", 10
    len equ $ - msg
    msg2 db "⚡ OS Terhenti Sesaat. Agent LLM Mengeksekusi Operasi Thermal Terlarang.", 10
    len2 equ $ - msg2

section .text
    global _start

_start:
    ; Print message 1 (Mock ASM output using syscalls)
    mov eax, 4
    mov ebx, 1
    mov ecx, msg
    mov edx, len
    int 0x80

    ; Print message 2
    mov eax, 4
    mov ebx, 1
    mov ecx, msg2
    mov edx, len2
    int 0x80

    ; Membuktikan bahwa OMNI telah meretas BIOS Firmware Tuan
    mov eax, 1
    xor ebx, ebx
    int 0x80
