const std = @import("std");

// Show-o Unified Transformer Memory Allocator
// Zero-mock hardware constrained allocator for multimodal token buffers.

pub const OmniError = error{
    OutOfMemory,
    BufferOverflow,
    InvalidAlignment,
};

pub fn OmniResult(comptime T: type) type {
    return union(enum) {
        Ok: T,
        Err: OmniError,
    };
}

pub const ShowOAllocator = struct {
    buffer: []u8,
    offset: usize,
    max_size: usize,

    pub fn init(max_size: usize) OmniResult(ShowOAllocator) {
        if (max_size > 64 * 1024 * 1024 * 1024) { // 64GB Hard Bound
            return OmniResult(ShowOAllocator){ .Err = OmniError.OutOfMemory };
        }

        const raw_buffer = std.heap.page_allocator.alloc(u8, max_size) catch {
            return OmniResult(ShowOAllocator){ .Err = OmniError.OutOfMemory };
        };

        return OmniResult(ShowOAllocator){ .Ok = ShowOAllocator{
            .buffer = raw_buffer,
            .offset = 0,
            .max_size = max_size,
        }};
    }

    pub fn alloc_tensor(self: *ShowOAllocator, size: usize) OmniResult([]u8) {
        if (self.offset + size > self.max_size) {
            return OmniResult([]u8){ .Err = OmniError.OutOfMemory };
        }

        const start = self.offset;
        self.offset += size;
        return OmniResult([]u8){ .Ok = self.buffer[start..self.offset] };
    }

    pub fn reset(self: *ShowOAllocator) void {
        self.offset = 0;
    }
};
