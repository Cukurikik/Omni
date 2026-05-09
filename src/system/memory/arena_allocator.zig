//=============================================================================
// OMNI SYSTEM LAYER — ARENA ALLOCATOR (ZIG)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Bump-pointer arena allocator for extremely fast temporary 
//              tensor allocations during inference passes. O(1) allocation.
//=============================================================================

const std = @import("std");

pub const ArenaError = error{
    OutOfMemory,
};

/// A fast bump allocator for inference passes. Drops all memory at once.
pub struct TensorArena {
    buffer: []u8,
    offset: usize,
}

impl TensorArena {
    pub fn init(allocator: std.mem.Allocator, size: usize) !TensorArena {
        const buf = try allocator.alloc(u8, size);
        return TensorArena{
            .buffer = buf,
            .offset = 0,
        };
    }

    pub fn alloc(self: *TensorArena, bytes: usize, alignment: usize) ![*]u8 {
        // Align offset
        const align_mask = alignment - 1;
        self.offset = (self.offset + align_mask) & ~align_mask;

        if (self.offset + bytes > self.buffer.len) {
            return ArenaError.OutOfMemory;
        }

        const ptr = self.buffer.ptr + self.offset;
        self.offset += bytes;
        return ptr;
    }

    pub fn reset(self: *TensorArena) void {
        self.offset = 0; // O(1) free of entire arena
    }

    pub fn deinit(self: *TensorArena, allocator: std.mem.Allocator) void {
        allocator.free(self.buffer);
    }
}

// OMNI IDIOM: FFI Export
export fn omni_arena_create(size: usize) *TensorArena {
    // In production, uses global Omni allocator
    unreachable; 
}
