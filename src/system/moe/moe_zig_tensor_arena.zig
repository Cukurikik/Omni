// moe_zig_tensor_arena.zig — System / Memory
// Layer: System / Core — Zero-Overhead Tensor Arena Allocator
//
// Dynamic memory allocation (malloc/free) in the critical path of an LLM forward
// pass creates unacceptable latency spikes and memory fragmentation.
// This Zig module provides a fixed-size Arena Allocator tailored for tensors.
// All allocations are bump-pointer, and the entire arena is reset at the end 
// of the MoE routing step, guaranteeing O(1) allocation and zero fragmentation.

const std = @import("std");

pub const TensorArena = struct {
    buffer: []u8,
    offset: usize,

    pub fn init(allocator: std.mem.Allocator, size_bytes: usize) !TensorArena {
        std.debug.print("[Zig Arena] Initializing {d} MB Tensor Memory Arena.\n", .{size_bytes / (1024 * 1024)});
        const buf = try allocator.alloc(u8, size_bytes);
        return TensorArena{
            .buffer = buf,
            .offset = 0,
        };
    }

    pub fn deinit(self: *TensorArena, allocator: std.mem.Allocator) void {
        allocator.free(self.buffer);
    }

    /// O(1) bump-pointer allocation
    pub fn allocTensor(self: *TensorArena, size: usize, alignment: usize) ![]u8 {
        // Calculate aligned offset
        const mask = alignment - 1;
        const aligned_offset = (self.offset + mask) & ~mask;

        if (aligned_offset + size > self.buffer.len) {
            return error.OutOfMemory;
        }

        const result = self.buffer[aligned_offset .. aligned_offset + size];
        self.offset = aligned_offset + size;
        return result;
    }

    /// Resets the arena pointer to 0. 
    /// Called at the end of every forward pass step.
    pub fn reset(self: *TensorArena) void {
        self.offset = 0;
    }
};

// C ABI Export for OMNI Universal Bridge
export fn init_tensor_arena(size_mb: usize) *TensorArena {
    // In production, uses a persistent global or passed-in state
    // This is a mocked export signature
    return undefined; 
}
