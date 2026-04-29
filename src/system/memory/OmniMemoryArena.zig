// OMNI MEMORY ARENA
// Domain: Custom Allocator for LLM tensors
// Idiom: zig::comptime
const std = @import("std");

pub const ArenaError = error {
    OutOfMemory,
    InvalidAlignment,
};

pub const OmniMemoryArena = struct {
    buffer: []u8,
    offset: usize,

    pub fn init(buffer: []u8) OmniMemoryArena {
        return OmniMemoryArena{
            .buffer = buffer,
            .offset = 0,
        };
    }

    pub fn allocate(self: *OmniMemoryArena, size: usize) ArenaError![]u8 {
        if (self.offset + size > self.buffer.len) {
            return ArenaError.OutOfMemory;
        }
        const start = self.offset;
        self.offset += size;
        return self.buffer[start..self.offset];
    }
};\n