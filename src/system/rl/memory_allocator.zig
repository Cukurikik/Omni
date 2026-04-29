const std = @import("std");

// OMNI RL - Low-Latency Memory Allocator
// Strict system-layer memory management for RL Replay Buffers using Zig

const Error = error{
    OutOfMemory,
    InvalidAlignment,
};

pub const ArenaAllocator = struct {
    buffer: []u8,
    offset: usize,

    pub fn init(buffer: []u8) ArenaAllocator {
        return ArenaAllocator{
            .buffer = buffer,
            .offset = 0,
        };
    }

    pub fn alloc(self: *ArenaAllocator, comptime T: type, count: usize) Error![]T {
        const byte_count = count * @sizeOf(T);
        const alignment = @alignOf(T);
        
        // Calculate padding for alignment
        var padding: usize = 0;
        const current_addr = @intFromPtr(self.buffer.ptr) + self.offset;
        const remainder = current_addr % alignment;
        if (remainder != 0) {
            padding = alignment - remainder;
        }

        const total_size = byte_count + padding;

        if (self.offset + total_size > self.buffer.len) {
            return Error.OutOfMemory;
        }

        self.offset += padding;
        const result_ptr = @as([*]T, @ptrCast(@alignCast(self.buffer[self.offset..].ptr)));
        self.offset += byte_count;

        return result_ptr[0..count];
    }

    pub fn reset(self: *ArenaAllocator) void {
        self.offset = 0;
    }
};

// Test to verify monadic/Result-like error handling in Zig
test "allocator validation" {
    var memory: [1024]u8 = undefined;
    var arena = ArenaAllocator.init(&memory);
    
    // Valid allocation
    const floats = try arena.alloc(f32, 100);
    try std.testing.expect(floats.len == 100);
    
    // Force OOM
    const result = arena.alloc(f32, 1000);
    try std.testing.expectError(Error.OutOfMemory, result);
}
