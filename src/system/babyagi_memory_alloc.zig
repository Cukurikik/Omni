// OMNI System Layer - BabyAGI Allocator
const std = @import("std");

pub const MemError = error{ OutOfMemory };

pub const Result = union(enum) {
    Ok: []u8,
    Err: MemError,
};

pub fn allocate_context_window(allocator: std.mem.Allocator, tokens: usize) Result {
    const bytes = tokens * 4; // Approx 4 bytes per token
    const buffer = allocator.alloc(u8, bytes) catch {
        return Result{ .Err = MemError.OutOfMemory };
    };
    return Result{ .Ok = buffer };
}

pub fn free_context_window(allocator: std.mem.Allocator, buffer: []u8) void {
    allocator.free(buffer);
}
