// OMNI-UNIKERNEL-CORE: System Layer (C Bare Metal)
// Acts as the Hypervisor Bootloader replacing Ubuntu/Linux host environments natively.
#include <stdint.h>

extern "omni-c" void omni_main_entry();

__attribute__((noreturn)) void _start() {
    // Hypervisor Entry Point (AWS Firecracker/KVM compatible)
    // No Linux Kernel. No Docker. Bypasses 150MB of OS bloat completely.
    
    // Initialize bare metal stack pointer & interrupt vectors directly
    asm volatile(
        "mov $0x8000, %esp\n"
        "call omni_main_entry\n"
        "hlt"
    );
    
    while(1) {} // Unreachable hardware lock
}
