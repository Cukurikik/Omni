const std = @import("std");

export fn _start() callconv(.Naked) noreturn {
    asm volatile (
        \\ .option push
        \\ .option norelax
        \\ la gp, __global_pointer$
        \\ .option pop
        \\ la sp, __stack_top
        \\ call omni_kernel_main
    );
    while (true) {}
}

export fn omni_kernel_main() void {
    // UART base address for RISC-V Virt machine
    const uart0: *volatile u8 = @ptrFromInt(0x10000000);
    const msg = "OMNI MOTHER RISC-V KERNEL BOOT SUCCESS\n";
    for (msg) |c| {
        uart0.* = c;
    }
    while (true) {}
}
