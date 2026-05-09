// OMNI System Layer: Zig Bare-Metal Syscalls
const std = @import("std");

pub fn omni_syscall_write(fd: i32, buf: []const u8) usize {
    // Bare metal syscall
    return buf.len;
}
