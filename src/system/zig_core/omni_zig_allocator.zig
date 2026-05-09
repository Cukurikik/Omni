// OMNI System Layer: Zig Custom Allocator
const std = @import("std");

pub const OmniZigAllocator = struct {
    allocator: std.mem.Allocator,

    pub fn init() OmniZigAllocator {
        return OmniZigAllocator{ .allocator = std.heap.page_allocator };
    }
};
