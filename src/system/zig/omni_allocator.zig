const std = @import("std");

/// OMNI MOTHER: Global Allocator wrapper for FFI (Production Grade)
/// Exposes Zig's fast allocators to C/Rust bridges safely.
export fn omni_c_alloc(size: usize) ?*anyopaque {
    const alignment = 16;
    const slice = std.heap.c_allocator.alignedAlloc(u8, alignment, size) catch return null;
    return slice.ptr;
}

export fn omni_c_free(ptr: ?*anyopaque, size: usize) void {
    if (ptr) |p| {
        const slice = @as([*]align(16) u8, @alignCast(@ptrCast(p)))[0..size];
        std.heap.c_allocator.free(slice);
    }
}
