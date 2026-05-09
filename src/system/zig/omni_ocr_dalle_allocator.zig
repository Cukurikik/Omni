// OMNI Framework - Zig Custom Memory Allocator for Inverse DALL-E OCR
// Optimized for fast allocation/deallocation of image tensors.

const std = @import("std");

pub const OmniOcrAllocator = struct {
    allocator: std.mem.Allocator,
    arena: std.heap.ArenaAllocator,

    pub fn init(backing_allocator: std.mem.Allocator) OmniOcrAllocator {
        return OmniOcrAllocator{
            .allocator = backing_allocator,
            .arena = std.heap.ArenaAllocator.init(backing_allocator),
        };
    }

    pub fn deinit(self: *OmniOcrAllocator) void {
        self.arena.deinit();
    }

    pub fn allocator(self: *OmniOcrAllocator) std.mem.Allocator {
        return self.arena.allocator();
    }

    pub fn allocate_tensor(self: *OmniOcrAllocator, size: usize) ![]u8 {
        return self.allocator().alloc(u8, size);
    }
};
